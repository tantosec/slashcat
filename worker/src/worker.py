import json
import asyncio
import tempfile

from job import Job
from env_vars import MASKFILES_DIR, RULES_DIR, WORDLISTS_DIR


class Worker:
    def __init__(self, system):
        self.system = system
        self.job = None

    def job_in_progress(self):
        return self.job is not None and not self.job.is_finished()

    def ensure_running_job(self):
        if not self.job_in_progress():
            raise RuntimeError("There is no job running")

    async def start_job(self, jdata):
        if self.job_in_progress():
            raise RuntimeError("A job is already in progress")

        self.system.fs.clear_hashcat_pid()

        job = Job(
            self.system,
            jdata["hashes"],
            jdata["skip"],
            jdata["last_mask_len"],
            jdata["last_maskfile_ind"],
            jdata["potfile"],
            jdata["command_args"],
        )
        await job.start()

        # Only assign after job.start returns successfully
        self.job = job

    async def status(self):
        self.ensure_running_job()

        st = await self.job.get_status()

        if st is None:
            raise RuntimeError(
                "Hashcat did not respond to the status command in time. This may be caused by Hashcat having a slow start up, for example when using a large wordlist."
            )

        return {
            "success": True,
            "status": st,
            "maskfile_ind": self.job.maskfile_ind,
            "max_maskfile_ind": (
                len(self.job.mf_lines) if self.job.mf_lines is not None else 0
            ),
        }

    async def poll(self):
        if self.job is None:
            raise RuntimeError("There is no running or stopped job")

        return {
            "success": True,
            "finished": self.job.exit_code is not None,
            "exit_code": self.job.exit_code,
            "stderr": self.job.exit_stderr,
            "results": await self.job.get_results(),
            "warning": await self.job.get_warning(),
        }

    async def stop(self):
        self.ensure_running_job()

        await self.job.stop()

    async def kill(self):
        self.ensure_running_job()

        await self.job.kill()

    async def identify(self, hashes):
        return await self.system.hashcat.identify(hashes)

    async def example_hashes(self):
        return await self.system.hashcat.example_hashes()

    async def list_files_response(self, dir_path):
        return {
            "pretty_output": self.system.fs.ls_l_dir(dir_path),
            "array_output": self.system.fs.list_files_in_dir(dir_path),
        }

    async def list_wordlists(self):
        return await self.list_files_response(WORDLISTS_DIR)

    async def list_rules(self):
        return await self.list_files_response(RULES_DIR)

    async def list_maskfiles(self):
        return await self.list_files_response(MASKFILES_DIR)
