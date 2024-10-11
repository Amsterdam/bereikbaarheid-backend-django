def str_to_bool(boolstr):
    if not isinstance(boolstr, str):
        return False
    return boolstr.lower() in ("1", "t", "true")
