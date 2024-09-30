import argparse
from typing import IO


class ParseFailedException(Exception):
    pass


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ParseFailedException(
            f"Error when parsing command: {message}\n\n{self.format_help()}"
        )

    def print_help(self, file: IO[str] | None = None) -> None:
        raise ParseFailedException(self.format_help())
