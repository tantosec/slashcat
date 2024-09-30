import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase

import datetime


class TestChangePriority(CommandTestBase):
    async def test_change_priority_invalid(self):
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

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        self.assertEqual(
            await get_command_output("changepriority 1 invalid"),
            "Error: priority must be an integer.",
        )

    async def test_change_priority(self):
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

        self.assertEqual(
            await get_command_output("add -p 1337 e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )
        self.assertEqual(
            await get_command_output("add -p 31337 e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        self.assertEqual(
            await get_command_output("list"),
            MatchesRegex(r"Job 2 \(priority 31337.*\nJob 1 \(priority 1337"),
        )

        self.assertEqual(
            await get_command_output("changepriority 2 3"),
            "Successfully updated job 2 to have priority 3.",
        )

        self.assertEqual(
            await get_command_output("list"),
            MatchesRegex(r"Job 1 \(priority 1337.*\nJob 2 \(priority 3"),
        )


if __name__ == "__main__":
    unittest.main()
