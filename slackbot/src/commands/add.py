import json
import aiohttp
from chat_adapter.global_adapter import get_adapter
from constants import (
    ATTACHMENT_HASH,
    ADD_COMMAND,
    DEFAULT_WORDLIST,
    JOB_CONTROLS,
    LIST_COMMAND,
    MASKFILES_COMMAND,
    RULES_COMMAND,
    WORDLISTS_COMMAND,
)
from env_vars import SLACK_BOT_TOKEN
from commands.base.base_command import BaseCommand, CommandException, CommandRunArgs
from commands.util.autodetect_hashes import autodetect_hashes
from jobs.util import get_next_job_priority
from jobs.job import job_start
from models.hash import Hash
from models.job import Job
from models.job_hash import JobHash
from jobs.worker import get_rules, get_wordlists, get_maskfiles


class AddCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "Start a new cracking job"

    def setup_parser(self, parser):
        parser.add_argument(
            "hash",
            nargs="*",
            help=f"The hash to crack. To crack using a file, attach it to the message and specify '{ATTACHMENT_HASH}' as the hash (eg `{ADD_COMMAND} {ATTACHMENT_HASH}`)",
        )
        parser.add_argument(
            "-m", "--mode", required=False, help="The hashcat hash mode"
        )
        parser.add_argument(
            "-w",
            "--wordlist",
            required=False,
            help="The wordlist to use when cracking",
        )
        parser.add_argument(
            "-r",
            "--rule",
            action="append",
            default=[],
            help="The rule(s) to apply to the wordlist",
        )
        parser.add_argument(
            "-j",
            "--single_rule",
            required=False,
            help="Single hashcat rule to apply to every word in the wordlist",
        )
        parser.add_argument(
            "-b",
            "--bruteforce_mask",
            required=False,
            help=f"Enable mask bruteforce mode and use the provided mask as the bruteforce mask. Can also recieve a hcmask file from `{MASKFILES_COMMAND}`. Not valid when -w is supplied",
        )
        parser.add_argument(
            "-i",
            "--increment",
            action="store_true",
            help="In mask bruteforce mode, increment the length of the mask as each length is checked (as opposed to bruteforcing a fixed size)",
        )
        parser.add_argument(
            "--min_increment",
            required=False,
            help="Minimum length to start at in incremental mode",
        )
        for i in range(1, 5):
            parser.add_argument(
                f"-{i}",
                f"--custom_charset{i}",
                required=False,
                help=f"Define a custom charset which you can use with '?{i}' in the bruteforce mask",
            )
        parser.add_argument(
            "-p", "--priority", required=False, help="The priority of the job"
        )

    def get_additional_args(self, c: CommandRunArgs):
        cmdline = ""
        if c.args.wordlist is not None:
            cmdline += f"-w {c.args.wordlist} "
        for r in c.args.rule:
            cmdline += f"-r {r} "
        if c.args.priority is not None:
            cmdline += f"-p {c.args.priority} "
        if c.args.single_rule is not None:
            cmdline += f"-j {c.args.single_rule} "
        if c.args.bruteforce_mask is not None:
            cmdline += f"-b {c.args.bruteforce_mask} "
        if c.args.increment:
            cmdline += "-i "
        if c.args.min_increment:
            cmdline += f"--min_increment {c.args.min_increment} "
        for i in range(1, 5):
            curr_charset_name = f"custom_charset{i}"
            if vars(c.args)[curr_charset_name] is not None:
                cmdline += f"-{i} {vars(c.args)[curr_charset_name]} "
        cmdline += " ".join(c.args.hash)
        return cmdline

    async def validate_wordlist(self, wl):
        if not wl in (await get_wordlists())["array_output"]:
            raise CommandException(
                f"Wordlist `{wl}` is not a valid wordlist. Use `{WORDLISTS_COMMAND}` to list available wordlists."
            )

    async def validate_bruteforce_mask(self, bfmask):
        if not "?" in bfmask and not bfmask in (await get_maskfiles())["array_output"]:
            raise CommandException(
                f"Maskfile `{bfmask}` is not a valid maskfile. Use `{MASKFILES_COMMAND}` to list available maskfiles, or provide a mask directly using the `?` character."
            )

    async def validate_rules(self, c: CommandRunArgs):
        if len(c.args.rule) == 0:
            return

        rules_list = (await get_rules())["array_output"]
        for r in c.args.rule:
            if not r in rules_list:
                raise CommandException(
                    f"Rule {r} is not a valid rule. Use `{RULES_COMMAND}` to list available rules."
                )

    async def get_priority(self, c: CommandRunArgs):
        if c.args.priority is not None:
            try:
                return int(c.args.priority)
            except ValueError as e:
                raise CommandException("Error: priority must be a number") from e
        else:
            return get_next_job_priority()

    async def get_hashes(self, c: CommandRunArgs):
        hs = c.args.hash

        if len(hs) == 0:
            raise CommandException("No hashes specified...")

        if len(hs) == 1 and hs[0].upper() == ATTACHMENT_HASH:
            return (
                (await get_adapter().retrieve_attached_file(c.cmd_data))
                .strip()
                .splitlines()
            )

        return hs

    async def get_hash_mode(self, c: CommandRunArgs, hs: list[str]):
        if c.args.mode is not None:
            try:
                return int(c.args.mode)
            except ValueError as e:
                raise CommandException("Error: hash mode must be a number.") from e
        else:
            await c.respond("No hash mode specified. Trying to autodetect it...")

            hash_mode, example_hashes = await autodetect_hashes(
                hs, self.get_additional_args(c)
            )

            await c.respond(
                f"Successfully detected the hash as '{example_hashes[str(hash_mode)]['name']}' (Hash mode {hash_mode})."
            )

            return hash_mode

    async def run(self, c):
        if c.args.wordlist and c.args.bruteforce_mask:
            raise CommandException(
                "You cannot specify both a wordlist and a bruteforce mask!"
            )

        bruteforce_mode = c.args.bruteforce_mask is not None

        if not bruteforce_mode and c.args.increment:
            raise CommandException("--increment does not make sense in wordlist mode!")

        if not c.args.increment and c.args.min_increment:
            raise CommandException("--min_increment may only be used with --increment")

        wl = None if bruteforce_mode else (c.args.wordlist or DEFAULT_WORDLIST)
        if not bruteforce_mode:
            wl = c.args.wordlist or DEFAULT_WORDLIST
            await self.validate_wordlist(wl)
        else:
            await self.validate_bruteforce_mask(c.args.bruteforce_mask)

        await self.validate_rules(c)

        priority = await self.get_priority(c)
        hs = await self.get_hashes(c)
        hash_mode = await self.get_hash_mode(c, hs)

        min_increment = 0
        if c.args.min_increment is not None:
            try:
                min_increment = int(c.args.min_increment)
            except ValueError:
                raise CommandException("Invalid value for --min_increment")

        new_job = Job.create(
            owner_id=c.user_id,
            command_args_j=json.dumps(
                {
                    "hash_mode": hash_mode,
                    "wordlist": wl,
                    "bruteforce_mask": c.args.bruteforce_mask,
                    "increment": c.args.increment,
                    "rules": c.args.rule,
                    "single_rule": c.args.single_rule,
                    "custom_charset1": c.args.custom_charset1,
                    "custom_charset2": c.args.custom_charset2,
                    "custom_charset3": c.args.custom_charset3,
                    "custom_charset4": c.args.custom_charset4,
                }
            ),
            priority=priority,
            state="Q",
            last_seen_progress=0,
            last_restore_point=0,
            last_mask_len=min_increment,
            last_maskfile_ind=0,
            max_progress=0,
            max_maskfile_ind=0,
        )
        for h in hs:
            h_obj, _ = Hash.get_or_create(hash=h)
            JobHash.insert(job=new_job, hash=h_obj).execute()

        other_job = Job.get_running()

        if other_job is not None:
            await c.respond(
                f"Job {new_job.id} created with priority {priority}.\nUse `{LIST_COMMAND}` to view the job queue."
            )
        else:
            await c.respond(
                f"Job {new_job.id} created with priority {priority}!\nNo other jobs are currently running, so starting this job.\n{JOB_CONTROLS}"
            )

            await job_start(new_job)
