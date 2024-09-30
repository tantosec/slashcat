from commands.base.base_command import BaseCommand


class Subcommand(BaseCommand):
    def __init__(self, subcommands: dict[str, BaseCommand]):
        super().__init__()

        self.subparser_dest = f"{self.__class__.__name__}_name"
        self.subcommands = subcommands

    def setup_parser(self, parser):
        subparsers = parser.add_subparsers(dest=self.subparser_dest)

        for subcommand_name in self.subcommands:
            curr_subcommand = self.subcommands[subcommand_name]
            p = subparsers.add_parser(subcommand_name, help=curr_subcommand.get_help())
            curr_subcommand.setup_parser(p)

    async def run(self, c):
        subcommand = vars(c.args)[self.subparser_dest]
        if subcommand is not None:
            await self.subcommands[subcommand].run(c)
        else:
            await c.respond(
                "Available subcommands: "
                + ", ".join(self.subcommands.keys())
                + ". Run with `--help` to see more info."
            )
