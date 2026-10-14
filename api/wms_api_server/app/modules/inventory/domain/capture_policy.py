"""Optional operator snapshot is checked against current authoritative WMS settings."""
from typing import Any

def assert_capture_policy(payload: dict[str,Any],policy_version: int,profiles: dict[tuple[str,str],dict[str,Any]]) -> None:
    if "expected_policy_version" not in payload and "expected_profile_versions" not in payload:
        return
    expected=payload.get("expected_policy_version")
    if isinstance(expected,bool) or not isinstance(expected,int) or expected!=policy_version:
        raise ValueError("Operator marking policy snapshot is obsolete")
    raw=payload.get("expected_profile_versions")
    if not isinstance(raw,list) or len(raw)!=len(profiles):
        raise ValueError("Operator profile snapshot must cover every current profile")
    supplied={}
    for item in raw:
        if not isinstance(item,dict) or set(item)!={"system_code","profile_code","version","mode"} or not all(isinstance(value,str) for value in item.values()):
            raise ValueError("Exact operator profile snapshot required")
        key=(item["system_code"],item["profile_code"])
        if key in supplied:
            raise ValueError("Duplicate operator profile snapshot")
        supplied[key]={"version":item["version"],"mode":item["mode"]}
    if supplied!=profiles:
        raise ValueError("Operator marking profile version or scan mode is obsolete")
