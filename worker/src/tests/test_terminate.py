import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestTerminate(WorkerTestBase):
    async def test_hashcat_stop(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "900150983cd24fb0d6963f7d28e17f72",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
        output_results = [
            "49f68a5c8493ec2c0bf489821c21fc3b:hi",
            "900150983cd24fb0d6963f7d28e17f72:abc",
        ]

        self.hashcat.mock_exit_code = -15
        await self.worker.start_job(
            {
                "hashes": input_hashes,
                "skip": 3,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": input_potfile,
                "command_args": {
                    "hash_mode": 0,
                    "wordlist": None,
                    "bruteforce_mask": "?l?l?l",
                    "increment": True,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
            },
        )

        self.hashcat.start.assert_called()

        await self.worker.stop()
        await self.finish_mock_hashcat_proc()

        self.hashcat.terminate.assert_called()
        self.assertEqual((await self.worker.poll())["finished"], True)

    async def test_hashcat_kill(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "900150983cd24fb0d6963f7d28e17f72",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
        output_results = [
            "49f68a5c8493ec2c0bf489821c21fc3b:hi",
            "900150983cd24fb0d6963f7d28e17f72:abc",
        ]

        self.hashcat.mock_exit_code = -9
        await self.worker.start_job(
            {
                "hashes": input_hashes,
                "skip": 3,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": input_potfile,
                "command_args": {
                    "hash_mode": 0,
                    "wordlist": None,
                    "bruteforce_mask": "?l?l?l",
                    "increment": True,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
            },
        )

        self.hashcat.start.assert_called()

        await self.worker.kill()
        await self.finish_mock_hashcat_proc()

        self.hashcat.kill.assert_called()
        self.assertEqual((await self.worker.poll())["finished"], True)


if __name__ == "__main__":
    unittest.main()
