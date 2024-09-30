from commands.list import ListCommand
from constants import LIST_COMMAND


class QueueAliasCommand(ListCommand):
    def get_help(self) -> str | None:
        return f"Alias for '{LIST_COMMAND}'"
