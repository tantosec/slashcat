import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase

import datetime


class TestList(CommandTestBase):
    async def test_list(self):
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

        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")
        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        list_output = await get_command_output("list")
        self.assertEqual(list_output, MatchesRegex(r"Job 1 [^\n]+RUNNING"))
        self.assertEqual(list_output, MatchesRegex(r"Job 2 [^\n]+QUEUED"))

    async def test_list_verbose(self):
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

        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")
        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        list_output = await get_command_output("list -v")
        self.assertEqual(
            list_output,
            MatchesRegex(r"1[^\n]+100[^\n]+RUNNING[^\n]+MD5[^\n]+50\.00%"),
        )
        self.assertEqual(
            list_output,
            MatchesRegex(r"1[^\n]+100[^\n]+RUNNING[^\n]+MD5[^\n]+50\.00%"),
        )


if __name__ == "__main__":
    unittest.main()
