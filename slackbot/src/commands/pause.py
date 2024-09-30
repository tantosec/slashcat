from commands.status import format_job_info
from constants import START_COMMAND
from commands.base.base_command import BaseCommand, CommandException
from jobs.job import job_pause
from models.job import Job


class PauseCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "Pauses the current running job"

    async def run(self, c):
        running_job = Job.get_running()
        if running_job is None:
            raise CommandException("Cannot pause job, there is no unpaused job!")
        else:
            await c.respond("Pausing current job...")

            status = await job_pause(running_job)

            job_info = await format_job_info(running_job, status)

            await c.respond(
                f"Current job paused!\n```\n{job_info}\n```\nUse `{START_COMMAND}` to start the job again."
            )
