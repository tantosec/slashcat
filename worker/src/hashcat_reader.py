import asyncio
import re


def remove_trailing_newline(x):
    return re.sub(r"\n$", "", x)


class HashcatReader:
    def __init__(self, base_reader: asyncio.StreamReader):
        self.base_reader = base_reader

        self.lines = []

        self.read_lock = False
        self.force_required = False

    def stop_unforced_reads(self):
        self.force_required = True

    def allow_unforced_reads(self):
        self.force_required = False

    async def clear(self, force=False):
        if self.force_required and not force:
            return

        await self.readlines()
        self.lines = []

    async def readlines(self):
        while self.read_lock:
            await asyncio.sleep(0.1)

        self.read_lock = True
        while 1:
            try:
                next_line = await asyncio.wait_for(self.base_reader.readline(), 0.1)
            except TimeoutError:
                break

            if next_line == b"":
                break
            next_line = remove_trailing_newline(next_line.decode())
            if next_line:
                self.lines.append(next_line)

        self.read_lock = False

    async def read_filtered(self, filt, force=False):
        if not force and self.force_required:
            return None

        await self.readlines()

        found = None
        for l in self.lines:
            if filt(l):
                found = l
                break

        if found is not None:
            self.lines.remove(found)
        return found

    async def read_remaining(self):
        await self.readlines()
        return "\n".join(self.lines)

    async def try_read_json(self, force=False):
        return await self.read_filtered(lambda x: x[0] == "{", force=force)

    async def try_read_nonjson(self, force=False):
        return await self.read_filtered(lambda x: x[0] != "{", force=force)
