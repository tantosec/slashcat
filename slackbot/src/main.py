#!/usr/bin/env python3
import asyncio
from healthcheck import run_healthcheck_server
from jobs.job import sync_worker_status
from models.setup_db import setup_db
from chat_adapter.global_adapter import get_adapter

setup_db()


async def main():
    await run_healthcheck_server()
    await sync_worker_status()

    await get_adapter().start()


if __name__ == "__main__":
    print("Starting crackbox...")
    asyncio.run(main())
