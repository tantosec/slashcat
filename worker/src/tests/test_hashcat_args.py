import re
import unittest
from unittest.mock import ANY

from hashcat_args import HashcatArgs
from mask import MaskfileLine


class MatchesRegex:
    def __init__(self, rgx):
        self.rgx = re.compile(rgx)

    def __repr__(self):
        return repr(self.rgx)

    def __eq__(self, other):
        return len(self.rgx.findall(other)) > 0


class TestHashcatArgs(unittest.TestCase):
    def test_wordlist_mode(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
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
            0,
            -1,
        )

        self.assertFalse(ha.is_bruteforce())
        self.assertEqual(
            ha.get_args(),
            [
                "--quiet",
                "--status-json",
                "--skip",
                "0",
                "--potfile-path",
                ANY,
                "-o",
                ANY,
                "-m",
                "1337",
                ANY,  # Hash path
                MatchesRegex(r"rockyou.txt$"),
            ],
        )

    def test_bruteforce_mode(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
                "wordlist": None,
                "bruteforce_mask": "?l?h?d",
                "increment": True,
                "rules": [],
                "single_rule": None,
                "custom_charset1": None,
                "custom_charset2": None,
                "custom_charset3": None,
                "custom_charset4": None,
            },
            0,
            0,
        )

        self.assertTrue(ha.is_bruteforce())
        self.assertEqual(
            ha.get_args(),
            [
                "--quiet",
                "--status-json",
                "-a",
                "3",
                "--skip",
                "0",
                "--potfile-path",
                ANY,
                "-o",
                ANY,
                "-m",
                "1337",
                ANY,  # Hash path
                "",
            ],
        )
        ha = ha.increase_increment()
        self.assertEqual(ha.get_args()[-1], "?l")
        ha = ha.increase_increment()
        self.assertEqual(ha.get_args()[-1], "?l?h")
        ha = ha.increase_increment()
        self.assertEqual(ha.get_args()[-1], "?l?h?d")

    def get_arg_val(self, args, target_arg):
        return args[args.index(target_arg) + 1]

    def test_skip(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
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
            1234,
            0,
        )

        args = ha.get_args()
        self.assertEqual(self.get_arg_val(args, "--skip"), "1234")

    def test_rules(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
                "wordlist": "rockyou.txt",
                "bruteforce_mask": None,
                "increment": False,
                "rules": ["a.rule", "b.rule"],
                "single_rule": None,
                "custom_charset1": None,
                "custom_charset2": None,
                "custom_charset3": None,
                "custom_charset4": None,
            },
            0,
            0,
        )

        args = ha.get_args()
        ind = args.index("-r")
        self.assertEqual(args[ind + 1], MatchesRegex("a.rule$"))
        self.assertEqual(args[ind + 2], "-r")
        self.assertEqual(args[ind + 3], MatchesRegex("b.rule$"))

    def test_single_rule(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
                "wordlist": "rockyou.txt",
                "bruteforce_mask": None,
                "increment": False,
                "rules": [],
                "single_rule": "testrule",
                "custom_charset1": None,
                "custom_charset2": None,
                "custom_charset3": None,
                "custom_charset4": None,
            },
            0,
            0,
        )

        args = ha.get_args()
        self.assertEqual(self.get_arg_val(args, "-j"), "testrule")

    def test_custom_charsets(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
                "wordlist": None,
                "bruteforce_mask": "?1?2?3?4",
                "increment": False,
                "rules": [],
                "single_rule": None,
                "custom_charset1": "cc1",
                "custom_charset2": "cc2",
                "custom_charset3": "cc3",
                "custom_charset4": "cc4",
            },
            0,
            0,
        )

        args = ha.get_args()
        self.assertEqual(self.get_arg_val(args, "-1"), "cc1")
        self.assertEqual(self.get_arg_val(args, "-2"), "cc2")
        self.assertEqual(self.get_arg_val(args, "-3"), "cc3")
        self.assertEqual(self.get_arg_val(args, "-4"), "cc4")

    def test_apply_mf_line(self):
        ha = HashcatArgs(
            {
                "hash_mode": 1337,
                "wordlist": None,
                "bruteforce_mask": "?1?2?3?4",
                "increment": False,
                "rules": [],
                "single_rule": None,
                "custom_charset1": "cc1",
                "custom_charset2": "cc2",
                "custom_charset3": "cc3",
                "custom_charset4": "cc4",
            },
            0,
            0,
        )

        ha = ha.apply_maskfile_line(MaskfileLine("override1,override2,?2?1"))
        args = ha.get_args()
        self.assertEqual(self.get_arg_val(args, "-1"), "override1")
        self.assertEqual(self.get_arg_val(args, "-2"), "override2")
        self.assertIn("?2?1", args)
        self.assertNotIn("cc3", args)
        self.assertNotIn("cc4", args)


if __name__ == "__main__":
    unittest.main()
