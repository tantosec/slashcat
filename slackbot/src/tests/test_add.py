import unittest
import asyncio
from unittest.mock import call

from tests.mock_chat_adapter import get_command_output
from tests.util import MatchesRegex
from tests.command_test_base import CommandTestBase


class TestAdd(CommandTestBase):
    async def test_add_simple(self):
        self.mock_worker["identify"].return_value = {"success": True, "result": ["0"]}
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        start_output = await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        self.mock_worker["identify"].assert_called_once_with(
            {"hashes": ["e07910a06a086c83ba41827aa00b26ed"]}
        )
        self.mock_worker["start_job"].assert_called_once_with(
            {
                "command_args": {
                    "hash_mode": "0",
                    "wordlist": "rockyou.txt",
                    "bruteforce_mask": None,
                    "increment": False,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
                "hashes": ["e07910a06a086c83ba41827aa00b26ed"],
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": [],
            }
        )

        self.assertIn(
            "No other jobs are currently running, so starting this job.",
            start_output,
        )

        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_has_calls(
            [
                call(MatchesRegex("no matches were found")),
                call(MatchesRegex("no more jobs")),
            ]
        )

    async def test_add_complex_wordlist(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        self.assertIn(
            "No other jobs are currently running, so starting this job.",
            await get_command_output(
                "add -r test1.rule -r test2.rule -p 123 -j testprefix -w test.txt e07910a06a086c83ba41827aa00b26ed"
            ),
        )

        self.mock_worker["identify"].assert_called_once_with(
            {"hashes": ["e07910a06a086c83ba41827aa00b26ed"]}
        )
        self.mock_worker["start_job"].assert_called_once_with(
            {
                "command_args": {
                    "hash_mode": "0",
                    "wordlist": "test.txt",
                    "bruteforce_mask": None,
                    "increment": False,
                    "rules": ["test1.rule", "test2.rule"],
                    "single_rule": "testprefix",
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
                "hashes": ["e07910a06a086c83ba41827aa00b26ed"],
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": [],
            }
        )

    async def test_add_complex_bruteforce(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        self.assertIn(
            "No other jobs are currently running, so starting this job.",
            await get_command_output(
                "add -b test?l?d?1?2?3?4 -i -1 asd -2 def -3 ghi -4 hij --min_increment 2 e07910a06a086c83ba41827aa00b26ed"
            ),
        )

        self.mock_worker["identify"].assert_called_once_with(
            {"hashes": ["e07910a06a086c83ba41827aa00b26ed"]}
        )
        self.mock_worker["start_job"].assert_called_once_with(
            {
                "command_args": {
                    "hash_mode": "0",
                    "wordlist": None,
                    "bruteforce_mask": "test?l?d?1?2?3?4",
                    "increment": True,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": "asd",
                    "custom_charset2": "def",
                    "custom_charset3": "ghi",
                    "custom_charset4": "hij",
                },
                "hashes": ["e07910a06a086c83ba41827aa00b26ed"],
                "skip": 0,
                "last_mask_len": 2,
                "last_maskfile_ind": 0,
                "potfile": [],
            }
        )

    async def test_invalid_wordlist(self):
        start_output = await get_command_output(
            "add -w invalid.txt e07910a06a086c83ba41827aa00b26ed"
        )

        self.assertEqual(start_output, MatchesRegex("not a valid wordlist"))
        self.mock_worker["start_job"].assert_not_called()

    async def test_add_no_wordlists(self):
        self.mock_worker["list_wordlists"].return_value = {
            "success": True,
            "wordlists": {
                "pretty_output": "",
                "array_output": [],
            },
        }

        start_output = await get_command_output("add e07910a06a086c83ba41827aa00b26ed")

        self.assertEqual(start_output, MatchesRegex("not a valid wordlist"))
        self.mock_worker["start_job"].assert_not_called()

    async def test_valid_maskfile(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        self.assertIn(
            "Job 1 created",
            await get_command_output(
                "add -b test1.hcmask e07910a06a086c83ba41827aa00b26ed"
            )
        )

    async def test_invalid_maskfile(self):
        self.assertEqual(
            await get_command_output(
                "add -b doesntexist.hcmask e07910a06a086c83ba41827aa00b26ed"
            ),
            "Maskfile `doesntexist.hcmask` is not a valid maskfile. Use `@Testbot maskfiles` to list available maskfiles, or provide a mask directly using the `?` character.",
        )

    async def test_invalid_rule(self):
        self.assertEqual(
            await get_command_output("add -r invalid e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex("not a valid rule"),
        )
        self.mock_worker["start_job"].assert_not_called()

    async def test_invalid_priority(self):
        self.assertEqual(
            await get_command_output("add -p test e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex("priority must be a number"),
        )
        self.mock_worker["start_job"].assert_not_called()

    async def test_invalid_hash_mode(self):
        self.assertEqual(
            await get_command_output("add -m test e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex("hash mode must be a number"),
        )
        self.mock_worker["start_job"].assert_not_called()

    async def test_invalid_hashes(self):
        self.assertEqual(
            await get_command_output("add"), MatchesRegex("No hashes specified")
        )
        self.mock_worker["start_job"].assert_not_called()

    async def test_invalid_argument_combinations(self):
        self.assertEqual(
            await get_command_output(
                "add -w test.txt -b ?a?a?a e07910a06a086c83ba41827aa00b26ed"
            ),
            MatchesRegex("cannot specify both a wordlist and a bruteforce mask"),
        )
        self.assertEqual(
            await get_command_output(
                "add -w test.txt -i e07910a06a086c83ba41827aa00b26ed"
            ),
            MatchesRegex("increment does not make sense"),
        )
        self.assertEqual(
            await get_command_output(
                "add -b ?a?a?a --min_increment 2 e07910a06a086c83ba41827aa00b26ed"
            ),
            MatchesRegex("--min_increment may only be used with --increment"),
        )

        self.mock_worker["start_job"].assert_not_called()

    async def test_invalid_min_increment(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }

        self.assertEqual(
            await get_command_output(
                "add -b ?a?a?a -i --min_increment a e07910a06a086c83ba41827aa00b26ed"
            ),
            MatchesRegex("Invalid value for --min_increment"),
        )
        self.mock_worker["start_job"].assert_not_called()

    async def test_add_attached(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        self.chat_adapter_mock.retrieve_attached_file.return_value = (
            "e07910a06a086c83ba41827aa00b26ed\n356a496ab51db7d18ab72f0efedb4516"
        )

        self.assertEqual(
            await get_command_output("add ATTACHED"),
            MatchesRegex(r"Job \d+ created"),
        )

        self.mock_worker["identify"].assert_called_once_with(
            {
                "hashes": [
                    "e07910a06a086c83ba41827aa00b26ed",
                    "356a496ab51db7d18ab72f0efedb4516",
                ]
            }
        )
        self.mock_worker["start_job"].assert_called_once_with(
            {
                "command_args": {
                    "hash_mode": "0",
                    "wordlist": "rockyou.txt",
                    "bruteforce_mask": None,
                    "increment": False,
                    "rules": [],
                    "single_rule": None,
                    "custom_charset1": None,
                    "custom_charset2": None,
                    "custom_charset3": None,
                    "custom_charset4": None,
                },
                "hashes": [
                    "e07910a06a086c83ba41827aa00b26ed",
                    "356a496ab51db7d18ab72f0efedb4516",
                ],
                "skip": 0,
                "last_mask_len": 0,
                "last_maskfile_ind": 0,
                "potfile": [],
            }
        )

    async def test_add_queue(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }
        self.mock_worker["start_job"].return_value = {"success": True}
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": [],
            "warning": None,
        }

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        # Poll twice, once for each
        await self.job_lifetime.run_poll()
        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_has_calls(
            [
                call(MatchesRegex("Job finished!")),
                call(MatchesRegex("Starting the next job in the queue")),
                call(MatchesRegex("Job finished!")),
                call(MatchesRegex("no more jobs in the queue")),
            ]
        )

    async def test_potfile(self):
        self.mock_worker["identify"].return_value = {
            "success": True,
            "result": ["0"],
        }
        self.mock_worker["start_job"].return_value = {"success": True}

        self.assertEqual(
            await get_command_output(
                "add e07910a06a086c83ba41827aa00b26ed 356a496ab51db7d18ab72f0efedb4516"
            ),
            MatchesRegex(r"Job \d+ created"),
        )

        self.assertEqual(
            await get_command_output(
                "add -w test.txt e07910a06a086c83ba41827aa00b26ed 356a496ab51db7d18ab72f0efedb4516"
            ),
            MatchesRegex(r"Job \d+ created"),
        )

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": False,
            "exit_code": None,
            "stderr": "",
            "results": [],
            "warning": None,
        }
        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_not_called()

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": False,
            "exit_code": None,
            "stderr": "",
            "results": ["e07910a06a086c83ba41827aa00b26ed:hashres1"],
            "warning": None,
        }
        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_has_calls(
            [MatchesRegex("Hash cracked: [^\n]+:hashres1")]
        )

        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": ["e07910a06a086c83ba41827aa00b26ed:hashres1"],
            "warning": None,
        }
        await self.job_lifetime.run_poll()

        self.chat_adapter_mock.send_message.assert_has_calls(
            [
                MatchesRegex(r"Hash cracked: [^\n]+:hashres1"),
                MatchesRegex(r"Job finished!.*:hashres1"),
                MatchesRegex("Starting the next job"),
                MatchesRegex(r"Hash found in potfile.*hashres1"),
            ]
        )

        # Check potfile was sent correctly
        self.assertEqual(
            self.mock_worker["start_job"].mock_calls[0].args[0]["potfile"], []
        )
        self.assertEqual(
            self.mock_worker["start_job"].mock_calls[1].args[0]["potfile"],
            ["e07910a06a086c83ba41827aa00b26ed:hashres1"],
        )

        # Finish job
        self.mock_worker["poll"].return_value = {
            "success": True,
            "finished": True,
            "exit_code": 1,
            "stderr": "",
            "results": ["e07910a06a086c83ba41827aa00b26ed:hashres1"],
            "warning": None,
        }
        await self.job_lifetime.run_poll()

        # Check job that is already in the potfile
        self.chat_adapter_mock.send_message.reset_mock()

        self.assertEqual(
            await get_command_output("add e07910a06a086c83ba41827aa00b26ed"),
            MatchesRegex(r"Job \d+ created"),
        )

        self.chat_adapter_mock.send_message.assert_has_calls(
            [
                MatchesRegex(r"Hash found in potfile.*hashres1"),
                MatchesRegex("job is already complete"),
            ]
        )


if __name__ == "__main__":
    unittest.main()
