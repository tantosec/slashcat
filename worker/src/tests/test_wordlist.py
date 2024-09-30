import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestWordlist(WorkerTestBase):
    async def test_basic_job(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "098f6bcd4621d373cade4e832627b4f6",
            "5bb50314c7d970ce6cb07afb583c4c9d",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
        output_results = [
            "49f68a5c8493ec2c0bf489821c21fc3b:hi",
            "098f6bcd4621d373cade4e832627b4f6:test",
            "5bb50314c7d970ce6cb07afb583c4c9d:pog",
        ]
        command_args = {
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

        self.fs.clear_hashcat_pid.assert_called()

        self.hashcat.start.assert_called_with(
            self.system, input_potfile, input_hashes, HashcatArgs(command_args, 3, 1)
        )

        self.assertEqual((await self.worker.poll())["finished"], False)

        self.fs.cleanup_files.assert_not_called()

        # Check results during execution
        self.fs.read_results.return_value = output_results[:2]
        self.assertEqual((await self.worker.poll())["results"], output_results[:2])

        # Finish job
        self.fs.read_results.return_value = output_results
        await self.finish_mock_hashcat_proc()

        self.assertEqual((await self.worker.poll())["finished"], True)
        self.fs.cleanup_files.assert_called()
        self.assertEqual((await self.worker.poll())["results"], output_results)


if __name__ == "__main__":
    unittest.main()
