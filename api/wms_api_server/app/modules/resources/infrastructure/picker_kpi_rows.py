"""Shared Oracle row and aware-instant decoding for one KPI snapshot."""
from datetime import datetime, timezone
from typing import Any


def rows(cursor: Any) -> list[dict[str, Any]]:
    keys = [column[0].lower() for column in cursor.description]
    return [dict(zip(keys, [item.read() if hasattr(item, "read") else item for item in row]))
        for row in cursor.fetchall()]


def instant(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Native aware instant required")
    return result.astimezone(timezone.utc)
