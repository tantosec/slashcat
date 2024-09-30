import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestExampleHashes(WorkerTestBase):
    async def test_hashcat_example_hashes(self):
        self.hashcat.example_hashes.return_value = "TESTEXAMPLEHASHES"

        self.assertEqual(await self.worker.example_hashes(), "TESTEXAMPLEHASHES")

        self.hashcat.example_hashes.assert_called()


if __name__ == "__main__":
    unittest.main()
