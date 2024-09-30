from commands.base.base_command import BaseCommand
from jobs.worker import kill_current_job


class KillCommand(BaseCommand):
    def get_help(self) -> str | None:
        return "Forcefully terminates the running job (use in case the bot breaks)."

    async def run(self, c):
        await c.respond("Sending kill signal to current job...")
        if await kill_current_job():
            await c.respond("Kill signal sent!")
        else:
            await c.respond(
                "Worker server failed to kill. Going to remove this job from the queue and hopefully that fixes things..."
            )
