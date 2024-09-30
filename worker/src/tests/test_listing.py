import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from tests.worker_util import WorkerTestBase


class TestListing(WorkerTestBase):
    async def test_list_wordlist(self):
        LS_L_OUTPUT = "-rw-------  1 user user   139921497 Apr 12 12:36 rockyou.txt"
        self.fs.ls_l_dir.return_value = LS_L_OUTPUT
        self.fs.list_files_in_dir.return_value = ["rockyou.txt"]

        self.assertEqual(
            await self.worker.list_wordlists(),
            {"pretty_output": LS_L_OUTPUT, "array_output": ["rockyou.txt"]},
        )

        self.fs.ls_l_dir.assert_called_once_with("./data/wordlists")
        self.fs.list_files_in_dir.assert_called_once_with("./data/wordlists")

    async def test_list_rules(self):
        LS_L_OUTPUT = "-rw-------  1 user user   139921497 Apr 12 12:36 test.rule"
        self.fs.ls_l_dir.return_value = LS_L_OUTPUT
        self.fs.list_files_in_dir.return_value = ["test.rule"]

        self.assertEqual(
            await self.worker.list_rules(),
            {"pretty_output": LS_L_OUTPUT, "array_output": ["test.rule"]},
        )

        self.fs.ls_l_dir.assert_called_once_with("./data/rules")
        self.fs.list_files_in_dir.assert_called_once_with("./data/rules")

    async def test_list_maskfiles(self):
        LS_L_OUTPUT = "-rw-------  1 user user   139921497 Apr 12 12:36 test.hcmask"
        self.fs.ls_l_dir.return_value = LS_L_OUTPUT
        self.fs.list_files_in_dir.return_value = ["test.hcmask"]

        self.assertEqual(
            await self.worker.list_maskfiles(),
            {"pretty_output": LS_L_OUTPUT, "array_output": ["test.hcmask"]},
        )

        self.fs.ls_l_dir.assert_called_once_with("./data/maskfiles")
        self.fs.list_files_in_dir.assert_called_once_with("./data/maskfiles")


if __name__ == "__main__":
    unittest.main()
