import os
import re
import subprocess

from system_interface.fs.fs_base import FsBase
from env_vars import HASH_PATH, POTFILE_PATH, RESULTS_PATH, STORAGE_DIR, MASKFILES_DIR


class Fs(FsBase):
    def __init__(self):
        pass

    def cleanup_files(self):
        for fname in [HASH_PATH, RESULTS_PATH, POTFILE_PATH]:
            try:
                os.unlink(fname)
            except FileNotFoundError:
                pass

    def read_maskfile(self, maskfile):
        with open(f"{MASKFILES_DIR}/{maskfile}", "r") as f:
            data = f.read()
        return data

    def write_potfile(self, potfile):
        with open(POTFILE_PATH, "w", encoding="utf8") as f:
            f.write("\n".join(potfile) + "\n")

    def write_hashfile(self, hashes):
        with open(HASH_PATH, "w", encoding="utf8") as f:
            f.write("\n".join(hashes) + "\n")

    def write_results(self, results):
        with open(RESULTS_PATH, "w", encoding="utf8") as f:
            f.write("\n".join(results) + "\n")

    def read_results(self):
        try:
            with open(RESULTS_PATH, "r", encoding="utf8") as f:
                return list(set(f.read().strip().splitlines()))
        except FileNotFoundError:
            return []

    def clear_hashcat_pid(self):
        try:
            os.remove(os.path.expanduser("~/.local/share/hashcat/sessions/hashcat.pid"))
            print("Successfully removed PID file")
        except OSError:
            pass

    def list_files_in_dir(self, dir_path):
        return [
            f"{re.sub(r'^' + re.escape(dir_path) + '/', '', dirpath + '/')}{filename}"
            for (dirpath, dirnames, filenames) in os.walk(dir_path)
            for filename in filenames
        ]

    def ls_l_dir(self, dir_path):
        return "\n".join(
            subprocess.check_output(["ls", "-lh", dir_path], stderr=subprocess.STDOUT)
            .decode()
            .strip()
            .splitlines()[1:]
        )
