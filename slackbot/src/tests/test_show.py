import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase

import datetime


class TestShow(CommandTestBase):
    async def test_show_not_in_db(self):
        self.assertEqual(
            await get_command_output("show e07910a06a086c83ba41827aa00b26ed"),
            "Could not find that hash in the database!",
        )

    async def test_show_in_db_but_no_result(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        await self.job_lifetime.run_poll()

        self.assertEqual(
            await get_command_output("show e07910a06a086c83ba41827aa00b26ed"),
            "The result for that hash is not in the potfile!",
        )

    async def test_show_successful(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 0,
            "stderr": "",
            "results": ["e07910a06a086c83ba41827aa00b26ed:testresult"],
            "warning": None,
        }

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        await self.job_lifetime.run_poll()

        self.assertEqual(
            await get_command_output("show e07910a06a086c83ba41827aa00b26ed"),
            "The result for that hash is `testresult`.",
        )


if __name__ == "__main__":
    unittest.main()
