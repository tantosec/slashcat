from commands.base.base_command import BaseCommand
from constants import EXAMPLE_RULE_COMMAND
from jobs.worker import get_rules
from commands.util.codeblock import create_codeblock


class RulesCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "List rules available to apply to wordlists"

    async def run(self, c):
        await c.respond(
            "The following rules are available:\n\n"
            + create_codeblock((await get_rules())["pretty_output"])
            + f"\nExample command using rule: `{EXAMPLE_RULE_COMMAND}`"
        )
