raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8");i=s.index('\ndef normalize_unit_scan_codes(')
s=s[:i]+'''\ndef normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]:
    from .domain.mark_identity import normalize_unit_scan_codes as normalize
    return normalize(scans)

__all__.append("normalize_unit_scan_codes")
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/domain/mark_identity.py");s=p.read_text(encoding="utf-8");s+='''\ndef normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]:
    """One canonical identity/hash contract for inventory and recipient commands."""
    from hashlib import sha256
    return [{"system_code":x["system_code"],"profile_code":x["profile_code"],
             "code_hash":sha256(canonical_mark(x["system_code"],x["profile_code"],x["code"])["identity"].encode("utf-8")).hexdigest()} for x in scans]
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8").replace('from ..public import normalize_unit_scan_codes','from ..domain.mark_identity import normalize_unit_scan_codes');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
