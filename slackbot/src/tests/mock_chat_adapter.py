from unittest.mock import Mock
from command_handler import handle_command


async def get_command_output(cmd_text):
    response = {"text": ""}

    async def respond(txt):
        if response["text"]:
            response["text"] += "\n"
        response["text"] += str(txt)

    await handle_command(
        "<@1337> " + cmd_text, "test_user_id", "test_channel", {}, respond
    )

    return response["text"]
