from dataclasses import dataclass
from system_interface.fs.fs_base import FsBase
from system_interface.fs.fs import Fs
from system_interface.hashcat.hashcat_base import HashcatBase
from system_interface.hashcat.hashcat import Hashcat


@dataclass
class SystemInterface:
    fs: FsBase
    hashcat: HashcatBase


def create_runtime_interface():
    return SystemInterface(Fs(), Hashcat())
