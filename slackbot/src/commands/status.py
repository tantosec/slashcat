import datetime
import json
from chat_adapter.global_adapter import get_adapter
from commands.util.display_shortened_hash import display_shortened_hash
from commands.util.format_progress import format_progress
from commands.util.custom_arg_parse import CustomArgumentParser
from constants import STATUS_COMMAND
from commands.base.base_command import BaseCommand, CommandException
from jobs.job import job_status
from jobs.util import parse_job_id
from jobs.worker import example_hashes
from models.job import Job


def format_delta(d: datetime.timedelta) -> str:
    if d.days < 0:
        return "Already finished"

    hours, r = divmod(d.seconds, 60 * 60)
    mins, secs = divmod(r, 60)

    parts = []
    if d.days != 0:
        parts.append(f"{d.days}d")
    if hours != 0:
        parts.append(f"{hours}h")
    if mins != 0:
        parts.append(f"{mins}m")
    if secs != 0:
        parts.append(f"{secs}s")

    if len(parts) == 0:
        parts.append("0s")

    return " ".join(parts)


def format_datetime(d: datetime.datetime):
    return d.strftime("%H:%M:%S, %d/%m/%Y")


async def format_job_info(job, status):
    r = []

    job_state_mapping = {
        "Q": "Queued",
        "R": "Running",
        "P": "Paused",
    }
    jd = json.loads(job.command_args_j)

    eh = await example_hashes()

    r.append(f"Job state:           {job_state_mapping[job.state]}")
    r.append(
        f"Owner:               {await get_adapter().user_id_to_name(job.owner_id)}"
    )
    hash_mode = f"{jd['hash_mode']} ({eh[str(jd['hash_mode'])]['name']})"
    r.append(f"Hash mode:           {hash_mode}")

    if jd["bruteforce_mask"]:
        r.append(f"Bruteforce mask:     {jd['bruteforce_mask']}")
        r.append(f"Is incremental:      {jd['increment']}")
    else:
        r.append(f"Wordlist:            {jd['wordlist']}")

    if jd["rules"]:
        r.append(f"Rules:               {', '.join(jd['rules'])}")
    if jd["single_rule"]:
        r.append(f"Single rule:         {jd['single_rule']}")
    for i in range(1, 5):
        k = f"custom_charset{i}"
        if jd[k]:
            r.append(f"Custom charset {i}:    {jd[k]}")

    for i, h in enumerate(job.get_hashes()):
        curr_h = display_shortened_hash(h.hash)
        if h.result is not None:
            curr_h += f" [CRACKED] --> {h.result}"
        if i == 0:
            r.append(f"Hashes:              {curr_h}")
        else:
            r.append(f"                     {curr_h}")
        if i >= 10:
            r.append("                     ...")
            break

    if job.last_seen_progress != 0:
        r.append(
            f"Progress:            {job.last_seen_progress} / {job.max_progress} ({format_progress(job.last_seen_progress, job.max_progress)})"
        )

    if status is not None:
        if jd["bruteforce_mask"]:
            if job.max_maskfile_ind != 0:
                r.append(
                    "Maskfile progress:   {} / {} ({:.2f}%)".format(
                        job.last_maskfile_ind,
                        job.max_maskfile_ind,
                        100 * job.last_maskfile_ind / job.max_maskfile_ind,
                    )
                )
            r.append(f"Current mask length: {status['guess']['guess_mask_length']}")

        now = datetime.datetime.now()
        start_time = datetime.datetime.fromtimestamp(status["time_start"])
        end_time = datetime.datetime.fromtimestamp(status["estimated_stop"])
        elapsed = now - start_time
        remaining = end_time - now

        r.append(f"Start time:          {format_datetime(start_time)}")
        r.append(f"Estimated end time:  {format_datetime(end_time)}")
        r.append(f"Elapsed time:        {format_delta(elapsed)}")
        r.append(f"Remaining time:      {format_delta(remaining)}")

        devices = ", ".join(
            [
                f"{dev['device_name']} ({dev['device_type']})"
                for dev in status["devices"]
            ]
        )
        r.append(f"Devices:             {devices}")

    return "\n".join(r)


class StatusCommand(BaseCommand):
    def setup_parser(self, parser: CustomArgumentParser):
        parser.add_argument(
            "job_id",
            nargs="?",
            help="The job_id of the job to get the status of. If blank, will use the current running job.",
        )

    def get_help(self) -> str | None:
        return "Displays the information for a job."

    async def run(self, c):
        running_job = Job.get_running()

        job = None
        if c.args.job_id is None:
            if running_job is None:
                await c.respond(
                    f"No jobs are running, please specify the job id. (eg `{STATUS_COMMAND} <job_id>`)"
                )
                return
            else:
                job = running_job
        else:
            job = parse_job_id(c.args.job_id)

        r = []

        status = None
        if running_job is not None and job.id == running_job.id:
            try:
                status = await job_status(running_job)
                job = Job.get_by_id(job.id)
            except CommandException as e:
                r.append(f"Failed to get status from the worker server:")
                r.append(str(e))
                r.append("")

        r.append(await format_job_info(job, status))

        await c.respond(f"Info for job {job.id}:\n```\n" + "\n".join(r) + "\n```")
