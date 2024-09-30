class FsBase:
    def __init__(self):
        pass

    def cleanup_files(self):
        raise NotImplementedError()

    def read_maskfile(self, maskfile):
        raise NotImplementedError()

    def write_potfile(self, potfile):
        raise NotImplementedError()

    def write_hashfile(self, hashes):
        raise NotImplementedError()

    def write_results(self, hashes):
        raise NotImplementedError()

    def read_results(self):
        raise NotImplementedError()

    def clear_hashcat_pid(self):
        raise NotImplementedError()

    def list_files_in_dir(self, dir_path):
        raise NotImplementedError()

    def ls_l_dir(self, dir_path):
        raise NotImplementedError()
