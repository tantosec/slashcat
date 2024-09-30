from env_vars import BOT_TAG

# Slack messages
ADD_COMMAND = f"{BOT_TAG} add"
LIST_COMMAND = f"{BOT_TAG} list"
PAUSE_COMMAND = f"{BOT_TAG} pause"
CANCEL_COMMAND = f"{BOT_TAG} cancel"
START_COMMAND = f"{BOT_TAG} start"
STATUS_COMMAND = f"{BOT_TAG} status"

WORDLISTS_COMMAND = f"{BOT_TAG} wordlists"
RULES_COMMAND = f"{BOT_TAG} rules"
MASKFILES_COMMAND = f"{BOT_TAG} maskfiles"

JOB_CONTROLS = f"""Use `{STATUS_COMMAND}` to view the job status.
Use `{LIST_COMMAND}` to view the job queue.
Use `{PAUSE_COMMAND}` to pause job execution.
Use `{CANCEL_COMMAND}` to cancel and discard the job."""

# Config
DEFAULT_WORDLIST = "rockyou.txt"
ATTACHMENT_HASH = "ATTACHED"

EXAMPLE_HASHES_BUFFER_LIMIT = 100 * 1024 * 1024

HEALTHCHECK_PORT = 3000

# Example commands
EXAMPLE_WORDLIST_COMMAND = f"{BOT_TAG} add -w {DEFAULT_WORDLIST} <HASH>"
EXAMPLE_RULE_COMMAND = f"{BOT_TAG} add -r OneRuleToRuleThemStill.rule <HASH>"
EXAMPLE_CHARSETS_COMMAND = f"{BOT_TAG} add -b ?l?l?l <HASH>"
EXAMPLE_MASKLIST_COMMAND = f"{BOT_TAG} add -b kaonashi.hcmask <HASH>"

# Strings
HASHCAT_CHARSETS = """
  ? | Charset
 ===+=========
  l | abcdefghijklmnopqrstuvwxyz [a-z]
  u | ABCDEFGHIJKLMNOPQRSTUVWXYZ [A-Z]
  d | 0123456789                 [0-9]
  h | 0123456789abcdef           [0-9a-f]
  H | 0123456789ABCDEF           [0-9A-F]
  s |  !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~
  a | ?l?u?d?s
  b | 0x00 - 0xff
""".strip()  # This should probably pull from hashcat but it probably wont change
