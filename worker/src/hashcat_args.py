import copy
from env_vars import (
    HASH_PATH,
    POTFILE_PATH,
    RESULTS_PATH,
    RULES_DIR,
    WORDLISTS_DIR,
)
from mask import split_mask


class HashcatArgs:
    def __init__(self, command_args, skip, increment_len):
        self.hash_mode = command_args["hash_mode"]
        self.wordlist = command_args["wordlist"]
        self.bruteforce_mask = command_args["bruteforce_mask"]
        self.rules = command_args["rules"]
        self.increment = command_args["increment"]
        self.single_rule = command_args["single_rule"]

        self.custom_charsets = [command_args[f"custom_charset{i}"] for i in range(1, 5)]

        self.skip = skip
        self.increment_len = increment_len

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return (
            self.hash_mode == other.hash_mode
            and self.wordlist == other.wordlist
            and self.bruteforce_mask == other.bruteforce_mask
            and self.rules == other.rules
            and self.increment == other.increment
            and self.single_rule == other.single_rule
            and self.custom_charsets == other.custom_charsets
            and self.skip == other.skip
            and self.increment_len == other.increment_len
        )

    def __repr__(self):
        return f"HashcatArgs{repr(self.get_args())}"

    def apply_maskfile_line(self, mf_line):
        new_obj = copy.copy(self)
        new_obj.bruteforce_mask = mf_line.mask
        new_obj.custom_charsets = [
            *mf_line.custom_charsets,
            *(None for _ in range(4 - len(mf_line.custom_charsets))),
        ]
        return new_obj

    def increase_increment(self):
        new_obj = copy.copy(self)
        new_obj.increment_len += 1
        return new_obj

    def is_bruteforce(self):
        return self.wordlist is None

    def get_curr_mask(self):
        if self.increment:
            return "".join(split_mask(self.bruteforce_mask)[: self.increment_len])
        return self.bruteforce_mask

    def get_cache_key(self):
        return (tuple(self.custom_charsets), self.get_curr_mask())

    def get_args(self):
        argv = []
        argv.append("--quiet")
        argv.append("--status-json")

        if self.is_bruteforce():
            argv.extend(["-a", "3"])

        argv.extend(["--skip", str(self.skip)])

        argv.extend(["--potfile-path", POTFILE_PATH])
        argv.extend(["-o", RESULTS_PATH])
        argv.extend(["-m", str(self.hash_mode)])

        if self.single_rule is not None:
            argv.extend(["-j", self.single_rule])

        for rule in self.rules:
            argv.extend(["-r", f"{RULES_DIR}/{rule}"])

        if self.is_bruteforce():
            for arg_i, arg_val in zip(range(1, 5), self.custom_charsets):
                if arg_val is not None:
                    argv.extend([f"-{arg_i}", arg_val])

        argv.append(HASH_PATH)

        if self.is_bruteforce():
            argv.append(self.get_curr_mask())
        else:
            argv.append(f"{WORDLISTS_DIR}/{self.wordlist}")

        return argv
