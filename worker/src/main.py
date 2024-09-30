import functools
from mask import InvalidMaskError, split_mask
from aiohttp import web
from system_interface.system import create_runtime_interface
from schemas import start_job_schema, identify_schema, validate_mask_schema
from schema import SchemaError
from worker import Worker


def make_err(reason):
    return web.json_response({"success": False, "reason": str(reason)})


def error_wrapper(func):
    @functools.wraps(func)
    async def wrapped(*args):
        try:
            return await func(*args)
        except Exception as e:
            print(e)
            return make_err(e)

    return wrapped


worker = Worker(create_runtime_interface())

routes = web.RouteTableDef()


@routes.get("/health")
async def healthcheck(_):
    return web.json_response({})


@routes.post("/start_job")
@error_wrapper
async def start_job(request):
    global global_job

    jdata = await request.json()
    jdata = start_job_schema.validate(jdata)

    await worker.start_job(jdata)

    return web.json_response({"success": True})


@routes.post("/status")
@error_wrapper
async def status(_):
    return web.json_response(await worker.status())


@routes.post("/poll")
@error_wrapper
async def poll(_):
    return web.json_response(await worker.poll())


@routes.post("/stop")
@error_wrapper
async def stop(_):
    await worker.stop()

    return web.json_response({"success": True})


@routes.post("/kill")
@error_wrapper
async def kill(_):
    await worker.kill()

    return web.json_response({"success": True})


@routes.post("/identify")
@error_wrapper
async def identify(request):
    jdata = await request.json()

    hashes = identify_schema.validate(jdata)["hashes"]

    return web.json_response({"success": True, "result": await worker.identify(hashes)})


@routes.post("/example_hashes")
@error_wrapper
async def example_hashes(_):
    return web.json_response(
        {"success": True, "example_hashes": await worker.example_hashes()}
    )


@routes.post("/list_wordlists")
@error_wrapper
async def list_wordlists(_):
    return web.json_response(
        {"success": True, "wordlists": await worker.list_wordlists()}
    )


@routes.post("/list_rules")
@error_wrapper
async def list_rules(_):
    return web.json_response({"success": True, "rules": await worker.list_rules()})


@routes.post("/list_maskfiles")
@error_wrapper
async def list_maskfiles(_):
    return web.json_response(
        {"success": True, "maskfiles": await worker.list_maskfiles()}
    )


app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=8000)
