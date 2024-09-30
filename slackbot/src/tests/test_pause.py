import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase

import datetime


class TestPause(CommandTestBase):
    async def test_pause(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}
        curr_time = datetime.datetime.now().timestamp()
        self.mock_worker["status"].return_value = {
            "success": True,
            "status": {
                "progress": [5, 10],
                "restore_point": 3,
                "guess": {"guess_mask_length": 0},
                "time_start": curr_time - 5,
                "estimated_stop": curr_time + 5,
                "devices": [{"device_name": "Test device", "device_type": "GPU"}],
            },
            "maskfile_ind": 0,
            "max_maskfile_ind": 0,
        }
        self.mock_worker["stop"].return_value = {"success": True}

        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        pause_output = await get_command_output("pause")
        self.assertIn("Current job paused!", pause_output)

        self.mock_worker["stop"].assert_called()
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 0,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        await self.job_lifetime.run_poll()

        start_output = await get_command_output("start 1")
        self.assertIn("Job 1 started!", start_output)

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }
        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_has_calls(
            [
                call(MatchesRegex("Job finished!")),
                call(MatchesRegex("no more jobs in the queue")),
            ]
        )


if __name__ == "__main__":
    unittest.main()
