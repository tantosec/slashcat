from prettytable import PrettyTable


def compact_table(headings, body):
    cols = transpose(body)

    i = 0
    while i < len(cols):
        if not any(cols[i]):
            del cols[i]
            del headings[i]
        else:
            i += 1

    tbl = PrettyTable(headings)
    tbl.add_rows(transpose(cols))
    return tbl.get_string()


def transpose(data):
    return list(zip(*data))
