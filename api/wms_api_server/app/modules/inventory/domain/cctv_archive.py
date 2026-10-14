"""CCTV archive bookmarks: pure formatting, no network access or credentials."""
from datetime import datetime, timedelta, timezone
from string import Formatter
from urllib.parse import quote, urlsplit

FIELDS = {"viewpoint", "cell", "from_iso", "to_iso"}

def validate_uri(uri: str) -> None:
    parsed = urlsplit(uri)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an HTTP(S) archive URL without embedded credentials")

def validate_template(template: str, offset: str) -> None:
    fields = set()
    for _, name, spec, conversion in Formatter().parse(template):
        if name is None:
            continue
        if name not in FIELDS or spec or conversion:
            raise ValueError("Archive placeholders: viewpoint, cell, from_iso, to_iso")
        fields.add(name)
    if not {"from_iso", "to_iso"} <= fields:
        raise ValueError("Archive template must locate both ends of the incident window")
    hours, minutes = map(int, offset[1:].split(":"))
    if hours > 14 or minutes > 59 or (hours == 14 and minutes):
        raise ValueError("Stored timestamp offset must be within 14 hours")
    validate_uri(template.format(**{key: "0" for key in FIELDS}))

def archive_uri(template: str, offset: str, created_at: datetime, cell: str, viewpoint: str,
                before: int, after: int) -> str:
    validate_template(template, offset)
    hours, minutes = map(int, offset[1:].split(":"))
    delta = timedelta(hours=hours, minutes=minutes) * (-1 if offset.startswith("-") else 1)
    moment = created_at.replace(tzinfo=timezone(delta)) if created_at.tzinfo is None else created_at
    values = {"cell": cell, "viewpoint": viewpoint,
              "from_iso": (moment - timedelta(seconds=before)).isoformat(),
              "to_iso": (moment + timedelta(seconds=after)).isoformat()}
    result = template.format(**{key: quote(value, safe="") for key, value in values.items()})
    validate_uri(result)
    return result
