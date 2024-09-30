import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase


class TestListing(CommandTestBase):
    async def test_empty_wordlists(self):
        self.mock_worker["list_wordlists"].return_value = {
            "success": True,
            "wordlists": {
                "pretty_output": "",
                "array_output": [],
            },
        }
        self.assertIn("(empty)", await get_command_output("wordlists"))

    async def test_listing_wordlists(self):
        self.assertIn(
            "PRETTY rockyou.txt\nPRETTY test.txt", await get_command_output("wordlists")
        )

    async def test_empty_rules(self):
        self.mock_worker["list_rules"].return_value = {
            "success": True,
            "rules": {
                "pretty_output": "",
                "array_output": [],
            },
        }
        self.assertIn("(empty)", await get_command_output("rules"))

    async def test_listing_rules(self):
        self.assertIn(
            "PRETTY test1.rule\nPRETTY test2.rule", await get_command_output("rules")
        )

    async def test_empty_maskfiles(self):
        self.mock_worker["list_maskfiles"].return_value = {
            "success": True,
            "maskfiles": {
                "pretty_output": "",
                "array_output": [],
            },
        }
        self.assertIn("(empty)", await get_command_output("maskfiles"))

    async def test_listing_maskfiles(self):
        self.assertIn(
            "PRETTY test1.hcmask\nPRETTY test2.hcmask",
            await get_command_output("maskfiles"),
        )


if __name__ == "__main__":
    unittest.main()
