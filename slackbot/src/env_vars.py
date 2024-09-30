import os
from dotenv import load_dotenv
import sys

load_dotenv(override=True)


def get_env(k, testing_val, verify=True):
    if "unittest" in sys.modules.keys():
        return testing_val
    res = os.environ.get(k)
    if res is None and verify:
        raise RuntimeError(f"Could not read env var {k}")
    return res


CHAT_APP = get_env("CHAT_APP", "testing")

SLACK_BOT_TOKEN = get_env("SLACK_BOT_TOKEN", None, verify=False)
SLACK_APP_TOKEN = get_env("SLACK_APP_TOKEN", None, verify=False)

DISCORD_BOT_TOKEN = get_env("DISCORD_BOT_TOKEN", None, verify=False)


SQLITE_PATH = get_env("SQLITE_PATH", ":memory:")
BOT_TAG = get_env("BOT_TAG", "@Testbot")

WORKER_URL = get_env("WORKER_URL", "http://shouldneverbeused")

ALLOWED_CHANNEL = get_env("ALLOWED_CHANNEL", "testchannel")
