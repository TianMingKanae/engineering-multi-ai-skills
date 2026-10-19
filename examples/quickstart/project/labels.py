"""Practice task: normalize a human-readable label to a stable key."""


def normalize_label(value: str) -> str:
    """Lowercase a label and replace its whitespace with hyphens."""
    return value.lower().replace(" ", "-")
