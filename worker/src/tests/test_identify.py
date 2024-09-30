import unittest
import asyncio
from dataclasses import dataclass
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine

from tests.worker_util import WorkerTestBase


class TestIdentify(WorkerTestBase):
    async def test_hashcat_identify(self):
        input_hashes = ["49f68a5c8493ec2c0bf489821c21fc3b"]

        self.hashcat.identify.return_value = "TESTIDENT"

        self.assertEqual(await self.worker.identify(input_hashes), "TESTIDENT")

        self.hashcat.identify.assert_called()


if __name__ == "__main__":
    unittest.main()
