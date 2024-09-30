from schema import Schema, Or

start_job_schema = Schema(
    {
        "command_args": {
            "hash_mode": int,
            "wordlist": Or(str, None),
            "bruteforce_mask": Or(str, None),
            "increment": bool,
            "rules": [str],
            "single_rule": Or(str, None),
            "custom_charset1": Or(str, None),
            "custom_charset2": Or(str, None),
            "custom_charset3": Or(str, None),
            "custom_charset4": Or(str, None),
        },
        "hashes": [str],
        "skip": int,
        "last_mask_len": int,
        "last_maskfile_ind": int,
        "potfile": [str],
    }
)


identify_schema = Schema({"hashes": [str]})

validate_mask_schema = Schema({"mask": str})
