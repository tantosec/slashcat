from chat_adapter.discord_chat_adapter import DiscordChatAdapter
from chat_adapter.slack_chat_adapter import SlackChatAdapter
from env_vars import CHAT_APP

_global_adapter = None


def get_adapter():
    global _global_adapter

    if _global_adapter is None:
        if CHAT_APP.lower().strip() == "discord":
            _global_adapter = DiscordChatAdapter()
        elif CHAT_APP.lower().strip() == "slack":
            _global_adapter = SlackChatAdapter()
        elif CHAT_APP.lower().strip() == "testing":
            # Will be mocked later
            _global_adapter = None
        else:
            raise NotImplementedError(f"Unrecognised chat app: '{CHAT_APP}'")

    return _global_adapter


def set_adapter(a):
    global _global_adapter
    _global_adapter = a
