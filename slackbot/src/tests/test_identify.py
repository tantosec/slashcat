import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase


class TestIdentify(CommandTestBase):
    async def test_identify_single_result(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}

        identify_output = await get_command_output(
            "identify e07910a06a086c83ba41827aa00b26ed"
        )

        self.mock_worker["identify"].assert_called_once_with(
            {"hashes": ["e07910a06a086c83ba41827aa00b26ed"]}
        )

        for i in ["Hash name: `MD5`", "Mode: `0`"]:
            self.assertIn(
                i,
                identify_output,
            )

    async def test_identify_multiple_result(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0", "10"],
        }

        identify_output = await get_command_output(
            "identify e07910a06a086c83ba41827aa00b26ed"
        )

        self.mock_worker["identify"].assert_called_once_with(
            {"hashes": ["e07910a06a086c83ba41827aa00b26ed"]}
        )

        for i in [
            "Hash name: `MD5`",
            "Mode: `0`",
            "Hash name: `md5($pass.$salt)`",
            "Mode: `10`",
        ]:
            self.assertIn(
                i,
                identify_output,
            )

    async def test_identify_multiple_query(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}

        identify_output = await get_command_output(
            "identify e07910a06a086c83ba41827aa00b26ed 356a496ab51db7d18ab72f0efedb4516"
        )

        self.mock_worker["identify"].assert_called_once_with(
            {
                "hashes": [
                    "e07910a06a086c83ba41827aa00b26ed",
                    "356a496ab51db7d18ab72f0efedb4516",
                ]
            }
        )

        for i in ["Hash name: `MD5`", "Mode: `0`"]:
            self.assertIn(
                i,
                identify_output,
            )

    async def test_identify_no_matches(self):
        self.mock_worker["identify"].return_value = {
            "success": False,
            "reason": "Hashcat failed with exit code 255: No hash-mode matches the structure of the input hash.",
        }

        self.assertEqual(
            await get_command_output("identify asd"),
            "No hash-mode matches the structure of the input hash.",
        )


if __name__ == "__main__":
    unittest.main()
