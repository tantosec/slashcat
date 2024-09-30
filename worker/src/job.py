import asyncio
import json
from hashcat_args import HashcatArgs
from hashcat_reader import HashcatReader
from mask import parse_maskfile, split_mask, validate_mask_file
from system_interface.system import SystemInterface


class Job:
    def __init__(
        self,
        system: SystemInterface,
        hashes,
        skip,
        last_mask_len,
        last_maskfile_ind,
        potfile,
        command_args,
    ):
        self.system = system

        self.hashes = hashes
        self.last_mask_len = last_mask_len
        self.potfile = potfile
        self.args = HashcatArgs(command_args, skip, last_mask_len or 1)

        self.manually_stopped = False
        self.exit_code = None
        self.exit_stderr = None

        self.final_results = []

        self.increment_mode = self.args.increment

        self.mf_lines = None
        self.maskfile_ind = 0
        if self.args.is_bruteforce():
            # Validate mask
            if "?" in self.args.bruteforce_mask:
                split_mask(self.args.bruteforce_mask)
            else:
                validate_mask_file(self.system, self.args.bruteforce_mask)
                self.mf_lines = parse_maskfile(self.system, self.args.bruteforce_mask)
                self.maskfile_ind = last_maskfile_ind

        self.mask_cache = set()

        self.started_signal = None

    def is_finished(self):
        return self.exit_code is not None

    def get_max_increment(self):
        if not self.args.is_bruteforce():
            return -1
        if self.mf_lines is not None:
            return max(len(split_mask(line.mask)) for line in self.mf_lines)
        return len(split_mask(self.args.bruteforce_mask))

    async def run_hashcat(self):
        if self.args.is_bruteforce():
            cache_key = self.args.get_cache_key()
            if cache_key in self.mask_cache:
                # We have already processed this (usually only happens with hcmask + increment)
                # No need to do it twice.
                return 1
            self.mask_cache.add(cache_key)

        await self.system.hashcat.start(
            self.system, self.potfile, self.hashes, self.args
        )

        if self.started_signal is not None:
            self.started_signal.set()

        exit_code, _, exit_stderr = await self.system.hashcat.wait()
        self.exit_stderr = exit_stderr

        self.args.skip = 0  # Set for the next job

        return exit_code

    async def run_hashcat_maskfiles(self):
        if self.mf_lines is not None:
            exit_code = None

            while self.maskfile_ind < len(self.mf_lines):
                mf_line = self.mf_lines[self.maskfile_ind]

                self.args = self.args.apply_maskfile_line(mf_line)

                exit_code = await self.run_hashcat()

                if self.manually_stopped or exit_code != 1:
                    return exit_code

                self.maskfile_ind += 1

            self.maskfile_ind = 0

            return exit_code
        else:
            return await self.run_hashcat()

    async def run_hashcat_increment(self):
        if self.args.increment:
            exit_code = None

            while self.args.increment_len <= self.get_max_increment():
                exit_code = await self.run_hashcat_maskfiles()

                if self.manually_stopped or exit_code != 1:
                    return exit_code

                self.args = self.args.increase_increment()

            return exit_code
        else:
            return await self.run_hashcat_maskfiles()

    async def job_task(self):
        self.exit_code = await self.run_hashcat_increment()
        self.update_final_results()
        self.system.fs.cleanup_files()

    async def start(self):
        self.started_signal = asyncio.Event()
        asyncio.create_task(self.job_task())
        await self.started_signal.wait()

        self.started_signal = None

    async def get_status(self):
        return await self.system.hashcat.get_status()

    async def get_warning(self):
        return await self.system.hashcat.get_warning()

    def update_final_results(self):
        self.final_results = self.system.fs.read_results()

    async def get_results(self):
        if self.is_finished():
            return self.final_results
        return self.system.fs.read_results()

    async def stop(self):
        self.manually_stopped = True
        self.system.hashcat.terminate()

    async def kill(self):
        self.manually_stopped = True
        self.system.hashcat.kill()
