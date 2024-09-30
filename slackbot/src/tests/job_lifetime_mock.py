from unittest.mock import patch
import asyncio


queue = None
save_required = False


class MockJobTiming:
    async def await_next_poll(self):
        await queue.get()

    def is_save_required(self):
        global save_required

        if save_required:
            save_required = False
            return True

        return False


class JobLifetimeMock:
    def __init__(self):
        global queue
        queue = asyncio.Queue()

        self.patcher = patch("jobs.job.JobTiming", new=MockJobTiming)

    async def run_poll(self):
        await queue.put(1)

        # Wait an amount of time to hopefully allow the coroutine running the lifecycle to poll
        await asyncio.sleep(0.01)

    async def run_poll_with_save(self):
        global save_required
        save_required = True
        await self.run_poll()
        assert not save_required

    def start_patch(self):
        self.patcher.start()
        return self

    def stop_patch(self):
        self.patcher.stop()

        global queue
        queue = None
