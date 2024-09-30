import json
import asyncio
import traceback
import time
from chat_adapter.global_adapter import get_adapter
from commands.util.parse_hashcat_result import parse_hashcat_result
from jobs.worker import (
    start_job,
    get_status,
    poll,
    stop,
)
from constants import JOB_CONTROLS
from commands.base.base_command import CommandException
from jobs.util import handle_exit_code
from models.job import Job


class PollFinished:
    def __init__(self, poll_res, new_results):
        self.exit_code = poll_res["exit_code"]
        self.results = poll_res["results"]
        self.stderr = poll_res["stderr"]
        self.new_results = new_results

    def __str__(self) -> str:
        return f"PollFinished(exit_code={self.exit_code}, results={self.results}, stderr={self.stderr}, new_results={self.new_results})"


class PollInProgress:
    def __init__(self, poll_res, new_results):
        self.warning = poll_res["warning"]
        self.results = poll_res["results"]
        self.new_results = new_results

    def __str__(self) -> str:
        return f"PollFinished(warning={self.warning}, results={self.results}, new_results={self.new_results})"


async def job_start(job):
    command_args = json.loads(job.command_args_j)

    hashes = job.get_hashes()
    potfile = []

    for h in hashes:
        if h.result is not None:
            if job.state == "Q":
                await get_adapter().send_message(
                    f"Hash found in potfile: `{h.hash} -> {h.result}`. Going to skip cracking this...",
                )
            potfile.append(f"{h.hash}:{h.result}")

    if len(hashes) == len(potfile):
        await get_adapter().send_message(
            "This job is already complete, so it has been removed from the queue.",
        )
        job.delete_instance()

        await start_next_job()
    else:
        await start_job(
            {
                "command_args": command_args,
                "hashes": [h.hash for h in hashes],
                "skip": job.last_restore_point,
                "last_mask_len": job.last_mask_len,
                "last_maskfile_ind": job.last_maskfile_ind,
                "potfile": potfile,
            },
        )

        job.state = "R"
        job.save()

        start_lifecycle(job)


async def job_status(job):
    j_resp = await get_status()

    progress = j_resp["status"]["progress"][0]
    max_progress = j_resp["status"]["progress"][1]
    restore_point = j_resp["status"]["restore_point"]
    mask_len = j_resp["status"]["guess"]["guess_mask_length"]

    job.last_seen_progress = progress
    job.last_restore_point = restore_point
    job.last_mask_len = mask_len
    job.last_maskfile_ind = j_resp["maskfile_ind"]
    job.max_progress = max_progress
    job.max_maskfile_ind = j_resp["max_maskfile_ind"]
    job.save()

    return j_resp["status"]


async def job_pause(job):
    assert job.state == "R"

    # Getting the status will save the progress automatically
    status = await job_status(job)

    job.state = "P"
    job.save()

    await job_stop(job)

    return status


async def job_poll(job):
    poll_res = await poll()

    all_results = poll_res["results"]
    new_results = []

    job_hashes = job.get_hashes()

    for r in all_results:
        hash, result = parse_hashcat_result(job_hashes, r)
        if hash.result is None:
            hash.result = result
            hash.save()
            new_results.append(r)

    if poll_res["finished"]:
        return PollFinished(poll_res, new_results)
    else:
        return PollInProgress(poll_res, new_results)


async def job_stop(_):
    await stop()


# Timing controller, mockable during testing
class JobTiming:
    def __init__(self):
        self.last_save = time.time()

    async def await_next_poll(self):
        await asyncio.sleep(1)

    def is_save_required(self):
        if time.time() - self.last_save > 10:
            self.last_save = time.time()
            return True
        return False


async def job_lifecycle_body(job):
    try:
        job_status_prefix = f"<@{job.owner_id}> (job {job.id})\n"

        # Job in progress
        poll_resp = None
        timing = JobTiming()
        while 1:
            await timing.await_next_poll()

            poll_resp = await job_poll(job)

            for new_res in poll_resp.new_results:
                await get_adapter().send_message(
                    f"{job_status_prefix}Hash cracked: `{new_res}`"
                )

            if type(poll_resp) is not PollInProgress:
                break

            if poll_resp.warning is not None:
                await get_adapter().send_message(
                    f"Warning: Hashcat provided this unexpected message: `{poll_resp.warning}`"
                    + (
                        "\nThis probably means a hash was discarded from the hash list as it isn't the correct format."
                        if "Separator unmatched" in poll_resp.warning
                        else ""
                    ),
                )

            if timing.is_save_required():
                try:
                    await job_status(job)
                except CommandException as e:
                    print(
                        "Warning: failed to get status from worker during auto progress save:",
                        e,
                    )

        # Job finished
        assert type(poll_resp) is PollFinished

        if poll_resp.exit_code == -9:
            # Job was killed. Should have been already cleaned up
            await get_adapter().send_message("Job killed successfully!")
            return

        # Refresh job
        job = Job.get_by_id(job.id)

        if job.state == "P":
            return

        try:
            handle_exit_code(poll_resp.exit_code, poll_resp.stderr)
        except CommandException as e:
            job.delete_instance()
            raise e

        if len(poll_resp.results) > 0:
            formatted_results = "\n".join(poll_resp.results)
            await get_adapter().send_message(
                f"{job_status_prefix}Job finished! :+1:\nThe results are summarised as follows:\n```\n{formatted_results}\n```",
            )
        else:
            await get_adapter().send_message(
                f"{job_status_prefix}Job finished!\nUnfortunately, no matches were found :sob:\nMaybe try again with a different wordlist? (`-w` parameter)",
            )

        job.delete_instance()
    except Exception as e:
        raise e

    await start_next_job()


async def start_next_job():
    # Start the next job
    next_job = Job.get_first_in_queue()
    if next_job is None:
        await get_adapter().send_message("There are no more jobs in the queue.")
    else:
        await get_adapter().send_message(
            f"Starting the next job in the queue (job {next_job.id} created by {await get_adapter().user_id_to_name(next_job.owner_id)}).\n{JOB_CONTROLS}",
        )

        await job_start(next_job)


async def job_lifecycle_wrapper(job):
    try:
        await job_lifecycle_body(job)
    except CommandException as e:
        await get_adapter().send_message(e)
    except Exception:  # pylint: disable=broad-exception-caught
        print(traceback.format_exc())
        await get_adapter().send_message(
            "An uncaught error occurred! :sob:\nPlease check the logs for details.",
        )


def start_lifecycle(job):
    asyncio.create_task(job_lifecycle_wrapper(job))


# Note: not handling the case where the worker is running something
#       we aren't aware of (can this even happen??)
async def sync_worker_status():
    job = Job.get_running()

    if job is None:
        return

    needs_start_job = False
    try:
        await job_poll(job)
    except CommandException:
        needs_start_job = True

    if needs_start_job:
        await job_start(job)
    else:
        # The worker server is running the job. We need to monitor it
        start_lifecycle(job)
