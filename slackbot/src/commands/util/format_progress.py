def format_progress(prog, max_prog):
    if max_prog == 0:
        return "0.00%"
    return "{:.2f}%".format(100 * prog / max_prog)
