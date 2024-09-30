from commands.base.base_command import BaseCommand
from constants import EXAMPLE_WORDLIST_COMMAND
from jobs.worker import get_wordlists
from commands.util.codeblock import create_codeblock


class WordlistsCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "List wordlists available for cracking with"

    async def run(self, c):
        await c.respond(
            "The following wordlists are available:\n\n"
            + create_codeblock((await get_wordlists())["pretty_output"])
            + f"\nExample command using wordlist: `{EXAMPLE_WORDLIST_COMMAND}`"
        )
