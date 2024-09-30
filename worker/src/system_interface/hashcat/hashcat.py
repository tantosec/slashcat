import asyncio
import json
import tempfile
import os
from hashcat_reader import HashcatReader
from system_interface.hashcat.hashcat_base import HashcatBase


def hashcat_failed(exit_code, stderr):
    raise RuntimeError(
        f"Hashcat failed with exit code {exit_code}: {stderr.decode().rstrip()}"
    )


class Hashcat(HashcatBase):
    def __init__(self):
        self.proc = None
        self.reader = None

    async def start(self, system, potfile, hashes, args):
        system.fs.write_potfile(potfile)
        system.fs.write_hashfile(hashes)
        system.fs.write_results(potfile)

        self.proc = await asyncio.create_subprocess_exec(
            "hashcat",
            *args.get_args(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self.reader = HashcatReader(self.proc.stdout)

    async def wait(self):
        exit_code = await self.proc.wait()
        stdout = await self.reader.read_remaining()
        stderr = (await self.proc.stderr.read()).decode()
        self.proc = None
        self.reader = None
        return exit_code, stdout, stderr

    async def get_status(self):
        if self.reader is None:
            return None

        for _ in range(3):
            await self.reader.clear()

            for _ in range(3):
                self.proc.stdin.write(b"s")
                next_line = await self.reader.try_read_json()

                if next_line is not None:
                    return json.loads(next_line)

            await asyncio.sleep(0.5)

        return None

    async def get_warning(self):
        if self.reader is None:
            return None
        return await self.reader.try_read_nonjson()

    def terminate(self):
        try:
            self.proc.terminate()
        except ProcessLookupError:
            pass

    def kill(self):
        try:
            self.proc.kill()
        except ProcessLookupError:
            pass

    async def identify(self, hashes):
        h_file = tempfile.NamedTemporaryFile("w", delete=False)
        h_file.write("\n".join(hashes))
        h_file.close()

        p = await asyncio.create_subprocess_exec(
            "hashcat",
            "--quiet",
            "--machine-readable",
            "--identify",
            h_file.name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert p.stdout is not None
        assert p.stderr is not None

        stdout, stderr = await p.communicate()

        os.unlink(h_file.name)

        if p.returncode != 0:
            hashcat_failed(p.returncode, stderr)

        return [int(x) for x in stdout.decode().strip().splitlines()]

    async def example_hashes(self):
        p = await asyncio.create_subprocess_exec(
            "hashcat",
            "--quiet",
            "--machine-readable",
            "--example-hashes",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await p.communicate()

        if p.returncode != 0:
            hashcat_failed(p.returncode, stderr)

        return json.loads(stdout.decode())
