import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestBruteforce(WorkerTestBase):
    async def test_bruteforce_job(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "900150983cd24fb0d6963f7d28e17f72",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
        output_results = [
            "49f68a5c8493ec2c0bf489821c21fc3b:hi",
            "900150983cd24fb0d6963f7d28e17f72:abc",
        ]

        command_args = {
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
        }
        await self.worker.start_job(
            {
                "hashes": input_hashes,
                "skip": 3,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": input_potfile,
                "command_args": command_args,
            }
        )

        self.hashcat.mock_exit_code = 1

        self.hashcat.start.assert_called_with(
            self.system, input_potfile, input_hashes, HashcatArgs(command_args, 3, 1)
        )

        self.assertEqual((await self.worker.poll())["finished"], False)
        self.fs.cleanup_files.assert_not_called()

        # Increment once
        await self.finish_mock_hashcat_proc()
        self.hashcat.start.assert_called_with(
            self.system, input_potfile, input_hashes, HashcatArgs(command_args, 0, 2)
        )
        self.assertEqual((await self.worker.poll())["finished"], False)
        self.fs.cleanup_files.assert_not_called()

        # Increment final time
        await self.finish_mock_hashcat_proc()
        self.hashcat.start.assert_called_with(
            self.system, input_potfile, input_hashes, HashcatArgs(command_args, 0, 3)
        )
        self.assertEqual((await self.worker.poll())["finished"], False)
        self.fs.cleanup_files.assert_not_called()

        # Finish
        self.hashcat.mock_exit_code = 0
        self.fs.read_results.return_value = output_results
        await self.finish_mock_hashcat_proc()

        self.assertEqual((await self.worker.poll())["finished"], True)
        self.fs.cleanup_files.assert_called()
        self.assertEqual((await self.worker.poll())["results"], output_results)


if __name__ == "__main__":
    unittest.main()
