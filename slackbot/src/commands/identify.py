from commands.base.base_command import BaseCommand, CommandException
from commands.util.autodetect_hashes import (
    format_identification,
    autodetect_hashes,
)

NO_MATCH_MSG = "No hash-mode matches the structure of the input hash."


class IdentifyCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "Identify the hash type of a hash"

    def setup_parser(self, parser):
        parser.add_argument("hash", nargs="*", help="The hash(es) to identify")

    async def run(self, c):
        h = c.args.hash
        h_str = " ".join(h)

        try:
            detect_cleanly = await autodetect_hashes(h, h_str)
        except CommandException as e:
            if NO_MATCH_MSG in str(e):
                raise CommandException(NO_MATCH_MSG)
            raise e

        ident, example_hashes = detect_cleanly
        await c.respond(
            "Hashcat identified the hash as the following:\n\n"
            + format_identification(ident, example_hashes, h_str)
        )
