import aiohttp
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from chat_adapter.chat_adapter import ChatAdapter
from commands.base.base_command import CommandException
from commands.util.time_based_cache import time_based_cache
from env_vars import ALLOWED_CHANNEL, SLACK_BOT_TOKEN, SLACK_APP_TOKEN


@time_based_cache(60 * 60)
async def user_id_to_name_mapping(client):
    all_users = await client.users_list()
    mapping = {}
    for user in all_users["members"]:
        if "real_name" in user:
            mapping[user["id"]] = user["real_name"]

    return mapping


class SlackChatAdapter(ChatAdapter):
    def __init__(self):
        super().__init__()

        self.app = AsyncApp(
            token=SLACK_BOT_TOKEN,
        )

        # Avoid circular imports
        import command_handler

        async def handle_slack_event(body, say):
            if body["event"]["channel"] != ALLOWED_CHANNEL:
                await say(f"Please use <#{ALLOWED_CHANNEL}> to issue commands.")
                return

            async def respond(msg):
                await say(str(msg))

            await command_handler.handle_command(
                body["event"]["text"],
                body["event"]["user"],
                body["event"]["channel"],
                body,
                respond,
            )

        self.app.event("app_mention")(handle_slack_event)

    async def start(self):
        self.handler = AsyncSocketModeHandler(self.app, SLACK_APP_TOKEN)

        await self.handler.start_async()

    async def send_message_to_channel(self, channel_id, data):
        await self.app.client.chat_postMessage(channel=channel_id, text=str(data))

    async def user_id_to_name(self, uid):
        return (await user_id_to_name_mapping(self.app.client))[uid]

    async def retrieve_attached_file(self, cmd_data):
        if not "files" in cmd_data["event"]:
            raise CommandException(
                "Error: You specified that hashes should be read from an attached file, but you didn't attach anything! :thinking_face:"
            )

        if len(cmd_data["event"]["files"]) != 1:
            raise CommandException("Error: Please attach only one file.")

        file_info = cmd_data["event"]["files"][0]

        async with aiohttp.ClientSession() as sess:
            async with sess.get(
                file_info["url_private"],
                headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            ) as resp:
                file_data = await resp.text()

        return file_data
