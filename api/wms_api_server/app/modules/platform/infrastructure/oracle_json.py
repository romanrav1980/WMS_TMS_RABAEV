"""Decode Oracle native JSON values or text/LOB without double decoding."""
import json
from typing import Any

def read_oracle_json(value: Any) -> Any:
    raw=value.read() if hasattr(value,"read") else value
    if isinstance(raw,(str,bytes,bytearray)):return json.loads(raw)
    if isinstance(raw,(dict,list,int,float,bool)) or raw is None:return raw
    raise TypeError("Unsupported Oracle JSON representation")
