"""Legacy transport-type aliases, independent of HTTP and Oracle."""


def normalize_transport_type(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    aliases = {"газель": "5"}
    return aliases.get(normalized.lower(), normalized)
