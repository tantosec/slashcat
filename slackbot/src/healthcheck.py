from aiohttp import web
from constants import HEALTHCHECK_PORT


async def healthcheck_route(_):
    return web.json_response({})


app = web.Application()
app.add_routes([web.get("/health", healthcheck_route)])


async def run_healthcheck_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=HEALTHCHECK_PORT)
    await site.start()
