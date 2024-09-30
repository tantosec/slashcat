import asyncio
from commands.base.base_command import CommandException
from constants import ADD_COMMAND
from jobs.worker import (
    example_hashes,
    identify_hashes,
)


def format_identification(hash_mode, example_hashes, hash_cmd_args) -> str:
    return f"""
Hash name: `{example_hashes[str(hash_mode)]["name"]}`
Mode: `{hash_mode}`
To crack with this hash mode, use the following command in slack: `{ADD_COMMAND} -m {hash_mode} {hash_cmd_args}`
    """.strip()


async def autodetect_hashes(hs: list[str], hash_cmd_args: str):
    options, identification = await asyncio.gather(
        example_hashes(), identify_hashes(hs)
    )

    # Note: hashcat will fail if there were no matches
    if len(identification) == 1:
        return (identification[0], options)

    raise CommandException(
        "Hashcat suggests the hash mode could be one of the following:\n\n"
        + "\n\n".join(
            [
                format_identification(ident, options, hash_cmd_args)
                for ident in identification
            ]
        )
    )
