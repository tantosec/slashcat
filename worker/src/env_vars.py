import os
from dotenv import load_dotenv
import sys

load_dotenv()


def get_env(k, testing_val):
    if "unittest" in sys.modules.keys():
        return testing_val
    res = os.environ.get(k)
    if res is None:
        raise RuntimeError(f"Could not read env var {k}")
    return res


STORAGE_DIR = get_env("STORAGE_DIR", "./storage")
HASH_PATH = f"{STORAGE_DIR}/hashes"
RESULTS_PATH = f"{STORAGE_DIR}/results"
POTFILE_PATH = f"{STORAGE_DIR}/tmp.pot"
WORDLISTS_DIR = get_env("WORDLISTS_DIR", "./data/wordlists")
RULES_DIR = get_env("RULES_DIR", "./data/rules")
MASKFILES_DIR = get_env("MASKFILES_DIR", "./data/maskfiles")
