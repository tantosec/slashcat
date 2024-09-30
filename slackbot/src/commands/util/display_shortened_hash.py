def display_shortened_hash(h):
    if len(h) > 100:
        return h[:100] + "..."
    return h
