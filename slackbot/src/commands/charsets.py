from commands.base.base_command import BaseCommand
from constants import EXAMPLE_CHARSETS_COMMAND, HASHCAT_CHARSETS


class CharsetsCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "List charsets available to use when using mask bruteforce mode"

    async def run(self, c):
        await c.respond(
            "The following hashcat charsets are available:\n\n```\n"
            + HASHCAT_CHARSETS
            + "\n```\n"
            + f"Example command using masked bruteforce with charsets: `{EXAMPLE_CHARSETS_COMMAND}`"
        )
