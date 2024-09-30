from constants import JOB_CONTROLS, PAUSE_COMMAND
from commands.util.custom_arg_parse import CustomArgumentParser
from commands.base.base_command import BaseCommand, CommandException
from jobs.job import job_start
from jobs.util import parse_job_id
from models.job import Job


class StartCommand(BaseCommand):
    def setup_parser(self, parser: CustomArgumentParser):
        parser.add_argument(
            "job_id",
            nargs="?",
            help="The job_id of the job to start. If left blank will default to the job with the highest priority.",
        )

    def get_help(self) -> str | None:
        return "Starts a stopped or paused job. If the job is paused, this will resume the job."

    async def run(self, c):
        if Job.get_running() is not None:
            raise CommandException(
                f"Error: there is already a job running! Only one job may be run at once for performance reasons.\nUse `{PAUSE_COMMAND}` to pause the running job."
            )

        if c.args.job_id:
            job = parse_job_id(c.args.job_id)
        else:
            job = Job.get_first_in_queue()
            if job is None:
                raise CommandException(
                    "But there are no jobs in the queue :thinking_face:"
                )

        await job_start(job)
        await c.respond(f"Job {job.id} started!\n{JOB_CONTROLS}")
