from commands.util.custom_arg_parse import CustomArgumentParser
from commands.base.base_command import BaseCommand
from models.hash import Hash


class ShowCommand(BaseCommand):
    def setup_parser(self, parser: CustomArgumentParser):
        parser.add_argument(
            "hash",
            help="The hash to display the potfile result for.",
        )

    def get_help(self) -> str | None:
        return "Displays the potfile result for a hash."

    async def run(self, c):
        h = Hash.get_or_none(hash=c.args.hash)
        if h is None:
            await c.respond("Could not find that hash in the database!")
            return
        if h.result is None:
            await c.respond("The result for that hash is not in the potfile!")
            return
        await c.respond(f"The result for that hash is `{h.result}`.")
