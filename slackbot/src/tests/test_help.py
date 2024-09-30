import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase


class TestHelp(CommandTestBase):
    async def test_help(self):
        self.assertIn("usage: ", await get_command_output("--help"))


if __name__ == "__main__":
    unittest.main()
