import aiohttp
import ssl
import asyncio
from commands.base.base_command import CommandException
from commands.util.time_based_cache import time_based_cache
from env_vars import WORKER_URL
from models.job import Job
from chat_adapter.global_adapter import get_adapter
from constants import START_COMMAND
from jobs.request_worker import request_worker


async def identify_hashes(hs: list[str]):
    return (await request_worker("identify", {"hashes": hs}))["result"]


# Note: this function should only be called when the worker is running!
@time_based_cache(60 * 60)
async def example_hashes():
    return (await request_worker("example_hashes"))["example_hashes"]


async def get_wordlists():
    return (await request_worker("list_wordlists"))["wordlists"]


async def get_rules():
    return (await request_worker("list_rules"))["rules"]


async def get_maskfiles():
    return (await request_worker("list_maskfiles"))["maskfiles"]


# Failsafe method to stop running jobs
async def kill_current_job():
    running_job = Job.get_running()
    if running_job is not None:
        running_job.delete_instance()

    try:
        await request_worker("kill")
        return True
    except CommandException:
        return False


async def start_job(data):
    await request_worker("start_job", data)


async def get_status():
    return await request_worker("status")


async def poll():
    return await request_worker("poll")


async def stop():
    return await request_worker("stop")
