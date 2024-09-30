import json
from chat_adapter.global_adapter import get_adapter
from commands.util.compact_table import compact_table
from commands.util.format_progress import format_progress
from commands.util.custom_arg_parse import CustomArgumentParser
from constants import (
    ADD_COMMAND,
    CANCEL_COMMAND,
    STATUS_COMMAND,
    PAUSE_COMMAND,
    START_COMMAND,
)
from commands.base.base_command import BaseCommand
from jobs.worker import example_hashes
from models.job import Job
from jobs.job import job_status


STATE_TO_TEXT = {
    "R": "RUNNING",
    "P": "PAUSED",
    "Q": "QUEUED",
}


def get_prog(job):
    return f"{format_progress(job.last_seen_progress,job.max_progress)}" + (
        f" (recovered {len(job.get_results())}/{len(job.hashes)})"
        if len(job.hashes) > 1
        else ""
    )


def get_mask_len(job, use_prefix=False):
    return (
        (" - mask length " if use_prefix else "") + str(job.last_mask_len)
        if json.loads(job.command_args_j)["bruteforce_mask"] is not None
        else ""
    )


class ListCommand(BaseCommand):
    def setup_parser(self, parser: CustomArgumentParser):
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Display a detailed table format",
        )

    def get_help(self) -> str | None:
        return "Displays the job queue."

    async def run(self, c):
        all_jobs = Job.select().order_by(Job.priority.desc())

        response = ""

        if len(all_jobs) == 0:
            response += "The job queue is currently empty.\n"
            response += f"Use `{ADD_COMMAND}` to create a new cracking job."
        else:
            running_job_exists = False

            response += "The job queue is as follows:\n"

            if c.args.verbose:
                headings = [
                    "ID",
                    "Priority",
                    "Owner",
                    "State",
                    "Mode",
                    "Wordlist/Mask",
                    "Rules",
                    "Single Rule",
                    "Progress",
                    "Mask length",
                ]

                eh = await example_hashes()

                rows = []
                for job in all_jobs:
                    if job.state == "R":
                        running_job_exists = True
                        await job_status(job)
                        job = Job.get_by_id(job.id)

                    jd = json.loads(job.command_args_j)

                    r = []
                    r.append(str(job.id))
                    r.append(job.priority)
                    r.append(await get_adapter().user_id_to_name(job.owner_id))
                    r.append(STATE_TO_TEXT[job.state])
                    r.append(eh[str(jd["hash_mode"])]["name"])
                    if jd["bruteforce_mask"]:
                        r.append(
                            jd["bruteforce_mask"] + " (incremental)"
                            if jd["increment"]
                            else ""
                        )
                    else:
                        r.append(jd["wordlist"])
                    r.append(",".join(jd["rules"]))
                    r.append(jd["single_rule"] if jd["single_rule"] else "")
                    # Not displaying custom charsets, seems unnecessary

                    if job.state != "Q":
                        r.append(get_prog(job))
                        r.append(get_mask_len(job))
                    else:
                        r.append("")
                        r.append("")

                    rows.append(r)

                response += "```\n" + compact_table(headings, rows) + "```\n\n"
            else:
                response += "```\n"
                for job in all_jobs:
                    response += f"Job {job.id} (priority {job.priority}, {await get_adapter().user_id_to_name(job.owner_id)}) - {STATE_TO_TEXT[job.state]}"
                    if job.state != "Q":
                        response += f" - {get_prog(job)}"
                        response += get_mask_len(job, use_prefix=True)
                    response += "\n"
                response += "```\n\n"

            if running_job_exists:
                response += f"Use `{PAUSE_COMMAND}` to pause the running job, or `{CANCEL_COMMAND}` to cancel it.\n"
                response += f"Use `{STATUS_COMMAND}` to find out more information about the running job.\n"
            else:
                response += f"Use `{START_COMMAND}` to start a job (or resume it if it is paused).\n"
                response += f"Use `{STATUS_COMMAND} <job_id>` to find out more information about a specific job.\n"
            response += f"Use `{CANCEL_COMMAND} <job_id>` to remove a specific job from the queue."

        await c.respond(response)
