import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase


class TestJob(CommandTestBase):
    async def test_warning(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}

        start_output = await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": False,
            "exit_code": None,
            "stderr": None,
            "results": [],
            "warning": "test warning",
        }

        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_called_once_with(
            MatchesRegex("test warning")
        )

    async def test_no_warning(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}

        start_output = await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": False,
            "exit_code": None,
            "stderr": None,
            "results": [],
            "warning": None,
        }

        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
