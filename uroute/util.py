def listify(x):
    """Puts ``x`` in a new list if it is not already a list. ``None`` returns
        an empty list."""
    if x is None:
        return []
    return x if isinstance(x, (list, tuple)) else [x]
