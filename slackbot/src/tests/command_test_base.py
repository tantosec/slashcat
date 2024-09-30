import unittest
from unittest.mock import patch, Mock, call

from tests.request_worker_mock import create_request_worker_mock
from tests.job_lifetime_mock import JobLifetimeMock

from chat_adapter import global_adapter
from chat_adapter.chat_adapter import ChatAdapter
from models.setup_db import setup_db, reset_db


class CommandTestBase(unittest.IsolatedAsyncioTestCase):
    def setUpClass():
        setup_db()

    def setUp(self):
        reset_db()

        self.mock_worker, mock_req_w = create_request_worker_mock()

        self.mock_worker["list_wordlists"].return_value = {
            "success": True,
            "wordlists": {
                "pretty_output": "PRETTY rockyou.txt\nPRETTY test.txt",
                "array_output": ["rockyou.txt", "test.txt"],
            },
        }

        self.mock_worker["list_rules"].return_value = {
            "success": True,
            "rules": {
                "pretty_output": "PRETTY test1.rule\nPRETTY test2.rule",
                "array_output": ["test1.rule", "test2.rule"],
            },
        }

        self.mock_worker["list_maskfiles"].return_value = {
            "success": True,
            "maskfiles": {
                "pretty_output": "PRETTY test1.hcmask\nPRETTY test2.hcmask",
                "array_output": ["test1.hcmask", "test2.hcmask"],
            },
        }

        self.worker_patcher = patch(
            "jobs.request_worker.request_endpoint_with_data", new=mock_req_w
        )
        self.worker_patcher.start()

        self.chat_adapter_mock = Mock(spec=ChatAdapter)
        global_adapter.set_adapter(self.chat_adapter_mock)

        self.job_lifetime = JobLifetimeMock()
        self.job_lifetime.start_patch()

    def tearDown(self):
        self.job_lifetime.stop_patch()
        self.worker_patcher.stop()
