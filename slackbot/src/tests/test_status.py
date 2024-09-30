import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase

import datetime

from models.job import Job


class TestStatus(CommandTestBase):
    async def test_status(self):
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

        status_output = await get_command_output("status")

        self.assertEqual(
            status_output,
            MatchesRegex(
                r"""Job state:           Running
Owner:               .*
Hash mode:           0 \(MD5\)
Wordlist:            rockyou.txt
Hashes:              e07910a06a086c83ba41827aa00b26ed
Progress:            5 / 10 \(50.00%\)
Start time:          .*
Estimated end time:  .*
Elapsed time:        5s
Remaining time:      4s
Devices:             Test device \(GPU\)"""
            ),
        )

        status_manual_output = await get_command_output("status 1")

        self.assertEqual(status_output, status_manual_output)

        self.assertEqual(
            await get_command_output("status 2"),
            MatchesRegex(
                r"""Job state:           Queued
Owner:               .*
Hash mode:           0 \(MD5\)
Wordlist:            rockyou.txt
Hashes:              e07910a06a086c83ba41827aa00b26ed"""
            ),
        )

    async def test_bruteforce_status(self):
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
            await get_command_output(
                "add -j ruleprefix -r test1.rule -r test2.rule -b ?a?a?a?a?1?2?3?4 -1 asd -2 def -3 ghi -4 hij -i e07910a06a086c83ba41827aa00b26ed"
            ),
            MatchesRegex(r"Job \d+ created"),
        )

        status_output = await get_command_output("status")
        self.maxDiff = None
        self.assertEqual(
            status_output,
            MatchesRegex(
                r"""Job state:           Running
Owner:               .*
Hash mode:           0 \(MD5\)
Bruteforce mask:     \?a\?a\?a\?a\?1\?2\?3\?4
Is incremental:      True
Rules:               test1.rule, test2.rule
Single rule:         ruleprefix
Custom charset 1:    asd
Custom charset 2:    def
Custom charset 3:    ghi
Custom charset 4:    hij
Hashes:              e07910a06a086c83ba41827aa00b26ed
Progress:            5 / 10 \(50.00%\)
Current mask length: 0
Start time:          .*
Estimated end time:  .*
Elapsed time:        5s
Remaining time:      4s
Devices:             Test device \(GPU\)"""
            ),
        )

    async def test_maskfile_status(self):
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
            "maskfile_ind": 3,
            "max_maskfile_ind": 10,
        }

        self.assertEqual(
            await get_command_output(
                "add -b test1.hcmask e07910a06a086c83ba41827aa00b26ed"
            ),
            MatchesRegex(r"Job \d+ created"),
        )

        status_output = await get_command_output("status")

        self.assertEqual(
            status_output,
            MatchesRegex(
                r"""Job state:           Running
Owner:               .*
Hash mode:           0 \(MD5\)
Bruteforce mask:     test1.hcmask
Is incremental:      False
Hashes:              e07910a06a086c83ba41827aa00b26ed
Progress:            5 / 10 \(50.00%\)
Maskfile progress:   3 / 10 \(30.00%\)
Current mask length: 0
Start time:          .*
Estimated end time:  .*
Elapsed time:        5s
Remaining time:      4s
Devices:             Test device \(GPU\)"""
            ),
        )

    async def test_saving(self):
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

        await self.job_lifetime.run_poll_with_save()

        # There isn't really a good way of simulating a server crash
        # so just check the database to see if it was saved
        self.assertEqual(Job.get_running().last_seen_progress, 5)
        self.assertEqual(Job.get_running().last_restore_point, 3)

    async def test_status_no_jobs(self):
        self.assertIn("No jobs are running", await get_command_output("status"))

        self.mock_worker["status"].assert_not_called()

    async def test_status_timedelta(self):
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
                "estimated_stop": curr_time + 60 * (60 * (24 * 4 + 3) + 2) + 2,
                "devices": [{"device_name": "Test device", "device_type": "GPU"}],
            },
            "maskfile_ind": 0,
            "max_maskfile_ind": 0,
        }

        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        status_output = await get_command_output("status")

        self.assertIn("4d 3h 2m 1s", status_output)

    async def test_less_than_second_timedelta(self):
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
                "estimated_stop": curr_time + 1,
                "devices": [{"device_name": "Test device", "device_type": "GPU"}],
            },
            "maskfile_ind": 0,
            "max_maskfile_ind": 0,
        }

        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        status_output = await get_command_output("status")

        self.assertIn("0s", status_output)

    async def test_already_finished_timedelta(self):
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
                "estimated_stop": curr_time - 1,
                "devices": [{"device_name": "Test device", "device_type": "GPU"}],
            },
            "maskfile_ind": 0,
            "max_maskfile_ind": 0,
        }

        await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        status_output = await get_command_output("status")

        self.assertIn("Already finished", status_output)

    async def test_cracked_hashes(self):
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

        await get_command_output(
            "add hash1 hash2 hash3 hash4 hash5 hash6 hash7 hash8 hash9 hash10 hash11"
        )

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": False,
            "exit_code": None,
            "stderr": "",
            "results": ["hash2:res2", "hash5:res5"],
            "warning": None,
        }

        await self.job_lifetime.run_poll()

        status_output = await get_command_output("status")

        self.assertEqual(
            status_output,
            MatchesRegex(
                r"""Job state:           Running
Owner:               .*
Hash mode:           0 \(MD5\)
Wordlist:            rockyou.txt
Hashes:              hash1
                     hash2 \[CRACKED\] --> res2
                     hash3
                     hash4
                     hash5 \[CRACKED\] --> res5
                     hash6
                     hash7
                     hash8
                     hash9
                     hash10
                     hash11
                     \.\.\.
Progress:            5 / 10 \(50.00%\)
Start time:          .*
Estimated end time:  .*
Elapsed time:        5s
Remaining time:      4s
Devices:             Test device \(GPU\)"""
            ),
        )


if __name__ == "__main__":
    unittest.main()
