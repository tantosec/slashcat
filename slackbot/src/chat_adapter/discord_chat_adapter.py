import aiohttp
import discord
from chat_adapter.chat_adapter import ChatAdapter
from commands.base.base_command import CommandException
from env_vars import ALLOWED_CHANNEL, DISCORD_BOT_TOKEN


class DiscordChatAdapter(ChatAdapter):
    def __init__(self):
        super().__init__()

        # Avoid circular imports
        import command_handler

        intents = discord.Intents.default()
        intents.message_content = True

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            print(f"Discord connected! {self.client.user}")

        @self.client.event
        async def on_message(msg):
            if self.client.user is None:
                return

            if msg.author == self.client.user:
                return

            if msg.channel.id != int(ALLOWED_CHANNEL):
                await msg.channel.send(
                    f"Please use <#{ALLOWED_CHANNEL}> to issue commands."
                )
                return

            mentioned_user = (
                len(msg.mentions) == 1 and msg.mentions[0].id == self.client.user.id
            )
            mentioned_role = any(
                [
                    r.name != "@everyone" and f"<@&{r.id}>" in msg.content
                    for r in msg.guild.get_member(self.client.user.id).roles
                ]
            )
            if not mentioned_user and not mentioned_role:
                return

            async def respond(txt):
                await msg.channel.send(str(txt))

            await command_handler.handle_command(
                msg.content, msg.author.id, msg.channel.id, msg, respond
            )

    async def start(self):
        await self.client.start(DISCORD_BOT_TOKEN)

    async def user_id_to_name(self, uid):
        u = await self.client.fetch_user(int(uid))
        return u.display_name

    async def send_message_to_channel(self, channel_id, data):
        chan = await self.client.fetch_channel(channel_id)
        assert type(chan) is discord.TextChannel
        await chan.send(data)  # pylint: disable

    async def retrieve_attached_file(self, cmd_data):
        if len(cmd_data.attachments) == 0:
            raise CommandException(
                "Error: You specified that hashes should be read from an attached file, but you didn't attach anything! :thinking_face:"
            )
        if len(cmd_data.attachments) > 1:
            raise CommandException("Error: Please attach only one file.")

        attach_url = cmd_data.attachments[0].url

        async with aiohttp.ClientSession() as sess:
            async with sess.get(attach_url) as resp:
                file_data = await resp.text()

        return file_data
