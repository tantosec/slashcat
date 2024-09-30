from argparse import Namespace
from dataclasses import dataclass
from typing import Awaitable, Callable, Any

from commands.util.custom_arg_parse import CustomArgumentParser

type RespondFunc = Callable[[str | Exception], Awaitable[None]]


@dataclass
class CommandRunArgs:
    cmd_text: str
    user_id: str
    channel_id: str
    args: Namespace
    respond: RespondFunc
    cmd_data: Any


# Exception for commands to respond with an error message
class CommandException(Exception):
    pass


class BaseCommand:
    def get_help(self) -> str | None:
        return None

    def setup_parser(self, parser: CustomArgumentParser):
        pass

    async def run(self, c: CommandRunArgs):
        raise NotImplementedError()
