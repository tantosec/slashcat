import re
from env_vars import MASKFILES_DIR


class InvalidMaskError(Exception):
    pass


def split_mask(mask):
    if not re.match(r"^(\?[ludhHsab1234?]|[^?])+$", mask):
        raise InvalidMaskError("Mask is incorrect format")
    return re.findall(r"\?[ludhHsab1234?]|[^?]", mask)


def validate_mask_file(system, mask):
    if not mask in system.fs.list_files_in_dir(MASKFILES_DIR):
        raise InvalidMaskError("Maskfile is incorrect")


class MaskfileLine:
    def __init__(self, line):
        self.line = line
        parts = re.split(r"(?<!\\),", line)
        try:
            for p in parts:
                split_mask(p)
        except InvalidMaskError:
            raise InvalidMaskError("Maskfile is not formatted correctly!")
        self.custom_charsets = parts[:-1]
        self.mask = parts[-1]


def parse_maskfile_from_str(maskfile_str):
    lines = maskfile_str.strip().splitlines()
    return [
        MaskfileLine(l) for l in lines if (not l.lstrip().startswith("#")) and l.strip()
    ]


def parse_maskfile(system, maskfile):
    data = system.fs.read_maskfile(maskfile)
    return parse_maskfile_from_str(data)
