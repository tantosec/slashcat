from commands.base.base_command import BaseCommand, CommandException
from commands.util.custom_arg_parse import CustomArgumentParser
from jobs.util import parse_job_id


class ChangePriorityCommand(BaseCommand):
    def setup_parser(self, parser: CustomArgumentParser):
        parser.add_argument(
            "job_id", help="The id of the job to change the priority of."
        )
        parser.add_argument("priority", help="The priority to set the job to.")

    def get_help(self) -> str | None:
        return "Changes the priority of a job."

    async def run(self, c):
        job = parse_job_id(c.args.job_id)

        try:
            priority = int(c.args.priority)
        except ValueError as e:
            raise CommandException("Error: priority must be an integer.") from e

        job.priority = priority
        job.save()

        await c.respond(
            f"Successfully updated job {job.id} to have priority {priority}."
        )
