from commands.status import StatusCommand
from constants import STATUS_COMMAND


class InfoAliasCommand(StatusCommand):
    def get_help(self) -> str | None:
        return f"Alias for '{STATUS_COMMAND}'"
