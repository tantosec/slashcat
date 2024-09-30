from constants import CANCEL_COMMAND, PAUSE_COMMAND
from commands.base.base_command import BaseCommand
from commands.util.custom_arg_parse import CustomArgumentParser
from jobs.job import job_stop
from jobs.util import parse_job_id
from models.job import Job


class CancelCommand(BaseCommand):
    def setup_parser(self, parser: CustomArgumentParser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Discard progress (Required if the job is running or paused)",
        )
        parser.add_argument(
            "job_id",
            nargs="?",
            help="The job_id of the job to cancel. If blank, will use the current running job.",
        )

    def get_help(self) -> str | None:
        return "Cancels a job, removing it from the queue."

    async def run(self, c):
        running_job = Job.get_running()

        if c.args.job_id is None or (
            running_job is not None and parse_job_id(c.args.job_id).id == running_job.id
        ):
            if running_job is None:
                await c.respond(
                    f"No jobs are running, please specify the job id. (eg `{CANCEL_COMMAND} <job_id>`)"
                )
            elif not c.args.force:
                resp = f"Are you sure you want to cancel the running job (job {running_job.id})?\n"
                resp += "This will discard job progress.\n"
                resp += f"If you are sure, use `{CANCEL_COMMAND} --force`.\n"
                resp += f"If you would rather pause the job, use `{PAUSE_COMMAND}`."
                await c.respond(resp)
            else:
                await c.respond("Stopping current job...")
                await job_stop(running_job)
        else:
            job = parse_job_id(c.args.job_id)

            assert job.state != "R"

            is_protected = job.state != "Q"

            if is_protected and not c.args.force:
                resp = "Are you sure you want to cancel this partially completed job?\n"
                resp += "This will discard job progress.\n"
                resp += f"If you are sure, use `{CANCEL_COMMAND} --force {job.id}`."
                await c.respond(resp)
            else:
                job.delete_instance()
                await c.respond(f"Removed job {job.id} from the queue.")
