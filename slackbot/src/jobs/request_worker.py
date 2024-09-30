import aiohttp
from env_vars import WORKER_URL
from commands.base.base_command import CommandException


async def request_endpoint_with_data(endpoint, data):
    async with aiohttp.ClientSession() as sess:
        async with sess.post(f"{WORKER_URL}/{endpoint}", json=data) as resp:
            if resp.status != 200:
                raise CommandException(
                    f"The worker server returned a non 200 status code ({resp.status})! :sob: Refer to the logs for details."
                )
            return await resp.json()


async def request_worker(endpoint, data=None):
    if data is None:
        data = {}

    j_resp = await request_endpoint_with_data(endpoint, data)

    if not j_resp["success"]:
        raise CommandException(f"The worker server threw an error: {j_resp['reason']}")

    return j_resp
