import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestErrors(WorkerTestBase):
    async def test_start_with_already_running(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "098f6bcd4621d373cade4e832627b4f6",
            "5bb50314c7d970ce6cb07afb583c4c9d",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
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

        with self.assertRaises(RuntimeError):
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

    async def test_poll_without_job(self):
        with self.assertRaises(RuntimeError):
            await self.worker.poll()

    async def test_stop_without_job(self):
        with self.assertRaises(RuntimeError):
            await self.worker.stop()

    async def test_kill_without_job(self):
        with self.assertRaises(RuntimeError):
            await self.worker.kill()


if __name__ == "__main__":
    unittest.main()
