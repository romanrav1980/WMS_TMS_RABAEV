"""Canonical content of a frozen review, shared without infrastructure cycles."""
from datetime import datetime
from hashlib import sha256
import json

def canonical(value: dict) -> str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def material(report: dict) -> tuple[str,str,datetime]:
    value=dict(report)
    captured=datetime.fromisoformat(value.pop("read_at_utc"))
    raw=canonical(value)
    return raw,sha256(raw.encode("utf-8")).hexdigest(),captured

