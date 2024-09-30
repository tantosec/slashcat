from peewee import fn, DoesNotExist
from commands.base.base_command import CommandException
from models.job import Job
from commands.util.codeblock import create_codeblock


def get_next_job_priority():
    min_priority = Job.select(fn.Min(Job.priority)).scalar()
    return 100 if min_priority is None else min_priority - 1


def parse_job_id(job_id_s: str):
    try:
        job_id = int(job_id_s)
    except ValueError:
        raise CommandException("Error: job_id must be a number")
    try:
        return Job.get_by_id(job_id)
    except DoesNotExist as e:
        raise CommandException(f"Error: job with id {job_id} does not exist!") from e


def handle_exit_code(exit_code, stderr):
    if exit_code == 0:
        return
    elif exit_code == 1:  # Wordlist exhausted
        assert stderr == ""
        return
    elif exit_code == -15:
        raise CommandException("Hashcat terminated successfully")
    elif exit_code == -9:
        raise CommandException("Hashcat killed successfully")
    else:
        raise CommandException(
            f"Hashcat exited with code {exit_code} and the following stderr:\n{create_codeblock(stderr)}"
        )
