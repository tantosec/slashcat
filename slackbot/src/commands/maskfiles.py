from commands.base.base_command import BaseCommand
from constants import EXAMPLE_MASKLIST_COMMAND
from jobs.worker import get_maskfiles
from commands.util.codeblock import create_codeblock


class MaskfilesCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "List mask files available to use instead of a mask"

    async def run(self, c):
        await c.respond(
            "The following mask files are available:\n\n"
            + create_codeblock((await get_maskfiles())["pretty_output"])
            + f"\nExample command using maskfile: `{EXAMPLE_MASKLIST_COMMAND}`"
        )
