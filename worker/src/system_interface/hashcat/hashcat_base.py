from hashcat_reader import HashcatReader


class HashcatBase:
    def __init__(self):
        pass

    async def start(self, system, potfile, hashes, args):
        raise NotImplementedError()

    async def wait(self):
        raise NotImplementedError()

    async def get_status(self):
        raise NotImplementedError()

    async def get_warning(self):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    async def identify(self, hashes):
        raise NotImplementedError()

    async def example_hashes(self):
        raise NotImplementedError()
