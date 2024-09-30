import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestStatus(WorkerTestBase):
    async def test_hashcat_status(self):
        input_hashes = ["49f68a5c8493ec2c0bf489821c21fc3b"]
        input_potfile = []
        output_results = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]

        await self.worker.start_job(
            {
                "hashes": input_hashes,
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": input_potfile,
                "command_args": {
                    "hash_mode": 0,
                    "wordlist": "rockyou.txt",
                    "bruteforce_mask": None,
                    "increment": False,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
            },
        )

        self.hashcat.get_status.return_value = "TEST_STATUS"
        self.assertEqual((await self.worker.status())["status"], "TEST_STATUS")

        await self.finish_mock_hashcat_proc()

    async def test_hashcat_status_returns_none(self):
        input_hashes = ["49f68a5c8493ec2c0bf489821c21fc3b"]
        input_potfile = []
        output_results = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]

        await self.worker.start_job(
            {
                "hashes": input_hashes,
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": input_potfile,
                "command_args": {
                    "hash_mode": 0,
                    "wordlist": "rockyou.txt",
                    "bruteforce_mask": None,
                    "increment": False,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
            },
        )

        self.hashcat.get_status.return_value = None

        with self.assertRaises(RuntimeError):
            await self.worker.status()

        await self.finish_mock_hashcat_proc()


if __name__ == "__main__":
    unittest.main()
