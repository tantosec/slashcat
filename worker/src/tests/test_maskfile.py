import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestMaskfile(WorkerTestBase):
    async def test_bruteforce_maskfile_job(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "900150983cd24fb0d6963f7d28e17f72",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
        output_results = [
            "49f68a5c8493ec2c0bf489821c21fc3b:hi",
            "900150983cd24fb0d6963f7d28e17f72:abc",
        ]

        self.fs.list_files_in_dir.return_value = ["test.hcmask"]
        self.fs.read_maskfile.return_value = "\n".join(
            ["?u?u?u", "?u?u", "?l?l", "?l?l?l", "?l?l?l?l", "?l?l?l?l?l"]
        )

        self.hashcat.mock_exit_code = 1
        command_args = {
            "hash_mode": 0,
            "wordlist": None,
            "bruteforce_mask": "test.hcmask",
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
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 2,
                "potfile": input_potfile,
                "command_args": command_args,
            },
        )

        self.fs.list_files_in_dir.assert_called_with("./data/maskfiles")
        self.fs.read_maskfile.assert_called_with("test.hcmask")

        expected_args = HashcatArgs(command_args, 0, ANY)
        self.hashcat.start.assert_called_with(
            self.system,
            input_potfile,
            input_hashes,
            expected_args.apply_maskfile_line(MaskfileLine("?l?l")),
        )

        self.assertEqual((await self.worker.poll())["finished"], False)
        self.fs.cleanup_files.assert_not_called()

        await self.finish_mock_hashcat_proc()
        self.hashcat.start.assert_called_with(
            self.system,
            input_potfile,
            input_hashes,
            expected_args.apply_maskfile_line(MaskfileLine("?l?l?l")),
        )

        self.assertEqual((await self.worker.poll())["finished"], False)
        self.fs.cleanup_files.assert_not_called()

        # This time, finish hashcat early
        self.hashcat.mock_exit_code = 0
        self.fs.read_results.return_value = output_results
        await self.finish_mock_hashcat_proc()

        self.assertEqual((await self.worker.poll())["finished"], True)
        self.fs.cleanup_files.assert_called()
        self.assertEqual((await self.worker.poll())["results"], output_results)

    async def test_hashcat_maskfile_increment(self):
        input_hashes = [
            "49f68a5c8493ec2c0bf489821c21fc3b",
            "900150983cd24fb0d6963f7d28e17f72",
        ]
        input_potfile = ["49f68a5c8493ec2c0bf489821c21fc3b:hi"]
        output_results = [
            "49f68a5c8493ec2c0bf489821c21fc3b:hi",
            "900150983cd24fb0d6963f7d28e17f72:abc",
        ]

        self.fs.list_files_in_dir.return_value = ["test.hcmask"]
        self.fs.read_maskfile.return_value = "\n".join(
            ["?u?u?u", "?u?u", "?l?l", "?l?l?l", "?l?l?l?l?l", "?l?l?l?l"]
        )

        self.hashcat.mock_exit_code = 1
        await self.worker.start_job(
            {
                "hashes": input_hashes,
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": input_potfile,
                "command_args": {
                    "hash_mode": 0,
                    "wordlist": None,
                    "bruteforce_mask": "test.hcmask",
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

        self.fs.list_files_in_dir.assert_called_with("./data/maskfiles")

        while not (await self.worker.poll())["finished"]:
            await self.finish_mock_hashcat_proc()

        self.assertEqual(
            [c[1][3].get_curr_mask() for c in self.hashcat.start.mock_calls],
            [
                "?u",
                "?l",
                "?u?u",
                "?l?l",
                "?u?u?u",
                "?l?l?l",
                "?l?l?l?l",
                "?l?l?l?l?l",
            ],
        )


if __name__ == "__main__":
    unittest.main()
