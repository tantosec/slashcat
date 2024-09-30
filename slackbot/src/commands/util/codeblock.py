def create_codeblock(data):
    data = str(data).strip()

    if len(data) == 0:
        return "```\n(empty)\n```"

    return "```\n" + data + "\n```"
