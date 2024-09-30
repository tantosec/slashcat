import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase

import datetime


class TestCancel(CommandTestBase):
    async def test_kill_job(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": False,
            "exit_code": None,
            "stderr": "",
            "results": [],
            "warning": None,
        }
        self.mock_worker["kill"].return_value = {"success": True}

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        self.assertEqual(
            await get_command_output("kill"),
            "Sending kill signal to current job...\nKill signal sent!",
        )

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": -9,
            "stderr": "",
            "results": [],
            "warning": None,
        }
        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_called_once_with(
            MatchesRegex("Job killed successfully!")
        )

    async def test_kill_with_no_job(self):
        self.mock_worker["kill"].return_value = {"success": True}

        self.assertEqual(
            await get_command_output("kill"),
            "Sending kill signal to current job...\nKill signal sent!",
        )


if __name__ == "__main__":
    unittest.main()
