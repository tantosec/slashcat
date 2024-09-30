import shlex
import traceback
import re
from commands.add import AddCommand
from commands.cancel import CancelCommand
from commands.changepriority import ChangePriorityCommand
from commands.charsets import CharsetsCommand
from commands.info_alias import InfoAliasCommand
from commands.kill import KillCommand
from commands.list import ListCommand
from commands.maskfiles import MaskfilesCommand
from commands.pause import PauseCommand
from commands.queue_alias import QueueAliasCommand
from commands.rules import RulesCommand
from commands.show import ShowCommand
from commands.start import StartCommand
from commands.status import StatusCommand
from commands.util.custom_arg_parse import ParseFailedException, CustomArgumentParser
from commands.wordlists import WordlistsCommand
from commands.base.base_command import BaseCommand, CommandException, CommandRunArgs
from commands.identify import IdentifyCommand
from env_vars import BOT_TAG

COMMANDS: dict[str, BaseCommand] = {
    "add": AddCommand(),
    "cancel": CancelCommand(),
    "changepriority": ChangePriorityCommand(),
    "status": StatusCommand(),
    "info": InfoAliasCommand(),
    "kill": KillCommand(),
    "list": ListCommand(),
    "queue": QueueAliasCommand(),
    "pause": PauseCommand(),
    "start": StartCommand(),
    "charsets": CharsetsCommand(),
    "maskfiles": MaskfilesCommand(),
    "rules": RulesCommand(),
    "wordlists": WordlistsCommand(),
    "identify": IdentifyCommand(),
    "show": ShowCommand(),
}

command_lock = False


async def handle_command(cmd_text, cmd_user_id, cmd_channel_id, cmd_data, respond):
    global command_lock

    parser = CustomArgumentParser(prog=BOT_TAG)
    subparsers = parser.add_subparsers(dest="subcommand_name")

    for cmd_name in COMMANDS:
        subparser = subparsers.add_parser(cmd_name, help=COMMANDS[cmd_name].get_help())

        COMMANDS[cmd_name].setup_parser(subparser)

    try:
        args_raw = shlex.split(cmd_text)
    except ValueError as e:
        await respond(f"Error when parsing command: {e}")
        return

    if not re.match(r"^<@.*>$", args_raw[0]):
        await respond(f"Error: the command must start with {BOT_TAG}")
        return

    args_raw = args_raw[1:]

    if len(args_raw) == 0:
        args_raw.append("--help")

    try:
        args = parser.parse_args(args_raw)
    except ParseFailedException as e:
        await respond(f"```\n{e}\n```")
        return

    c_args = CommandRunArgs(
        cmd_text,
        cmd_user_id,
        cmd_channel_id,
        args,
        respond,
        cmd_data,
    )

    if command_lock:
        await respond("Cannot run command - another command is currently in progress!")
        return

    command_lock = True

    try:
        await COMMANDS[args.subcommand_name].run(c_args)
    except CommandException as e:
        await respond(e)
    except Exception:  # pylint: disable=broad-exception-caught
        print(traceback.format_exc())
        await respond(
            "An uncaught error occurred! :sob:\nPlease check the logs for details."
        )

    command_lock = False
