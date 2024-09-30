from env_vars import ALLOWED_CHANNEL


class ChatAdapter:
    def __init__(self):
        pass

    async def start(self):
        raise NotImplementedError()

    async def send_message(self, data):
        await self.send_message_to_channel(ALLOWED_CHANNEL, data)

    async def send_message_to_channel(self, channel_id, data):
        raise NotImplementedError()

    async def user_id_to_name(self, uid):
        raise NotImplementedError()

    async def retrieve_attached_file(self, cmd_data):
        raise NotImplementedError()
