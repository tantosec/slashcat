import unittest
import asyncio
from unittest.mock import Mock
from worker import Worker
from system_interface.system import SystemInterface
from system_interface.fs.fs_base import FsBase
from system_interface.hashcat.hashcat_base import HashcatBase


def create_mock_fs():
    return Mock(spec=FsBase)


def create_mock_hashcat():
    mock_hashcat = Mock(spec=HashcatBase)
    mock_hashcat.mock_exit_code = 1
    mock_hashcat.mock_stdout = ""
    mock_hashcat.mock_stderr = ""

    mock_finish_signal = asyncio.Queue()

    async def wait_mock():
        await mock_finish_signal.get()

        return (
            mock_hashcat.mock_exit_code,
            mock_hashcat.mock_stdout,
            mock_hashcat.mock_stderr,
        )

    async def send_finish_signal():
        await mock_finish_signal.put(1)

    mock_hashcat.wait.side_effect = wait_mock

    return mock_hashcat, send_finish_signal


class WorkerTestBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.fs = create_mock_fs()
        self.hashcat, self.send_finish_signal = create_mock_hashcat()
        self.system = SystemInterface(self.fs, self.hashcat)
        self.worker = Worker(self.system)

    async def finish_mock_hashcat_proc(self):
        await self.send_finish_signal()
        await asyncio.sleep(0.01)
