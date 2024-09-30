class NoMatchingHashError(Exception):
    pass


def parse_hashcat_result(input_hashes, result):
    matching_hashes = [
        h for h in input_hashes if result.lower().startswith(h.hash.lower() + ":")
    ]
    if len(matching_hashes) != 1:
        raise NoMatchingHashError(input_hashes, result)
    return (matching_hashes[0], result[len(matching_hashes[0].hash) + 1 :])
