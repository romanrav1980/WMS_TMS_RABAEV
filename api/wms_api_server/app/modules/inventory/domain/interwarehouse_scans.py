"""Scanner evidence normalization; native Oracle resolves authoritative membership."""
from hashlib import sha256
from typing import Any
from .mark_identity import normalize_unit_scan_codes

def normalize_interwarehouse_scans(metadata: dict[str,Any]) -> dict[str,Any]:
    result=dict(metadata)
    scans=result.pop("scans",[])
    if scans:result["unit_scans"]=normalize_unit_scan_codes(scans)
    aggregations=result.get("aggregation_scans",[])
    if not aggregations:
        result.pop("aggregation_scans",None)
        return result
    normalized=[]
    if len(aggregations)>1000:raise ValueError("Maximum 1000 aggregation scans")
    for scan in aggregations:
        if set(scan)!={"system_code","profile_code","code","level"} or scan["level"]not in {"BOX","PALLET"}:
            raise ValueError("Exact aggregation scanner fields required")
        code=scan["code"]
        if not isinstance(code,str)or not code or len(code.encode("utf-8"))>4000 or "\x00"in code:
            raise ValueError("Invalid aggregation scanner code")
        normalized.append(dict(system_code=scan["system_code"],profile_code=scan["profile_code"],
                               level=scan["level"],code_hash=sha256(code.encode("utf-8")).hexdigest()))
    result["aggregation_scans"]=normalized
    return result
