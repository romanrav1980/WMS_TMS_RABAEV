raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='\ndef normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]:\n    """Shared canonical identity hashing for native exact profile coverage."""\n    from hashlib import sha256\n    from .domain.mark_identity import canonical_mark\n    return [{"system_code":x["system_code"],"profile_code":x["profile_code"],\n             "code_hash":sha256(canonical_mark(x["system_code"],x["profile_code"],x["code"])["identity"].encode("utf-8")).hexdigest()} for x in scans]\n\n__all__.append("normalize_unit_scan_codes")\n'
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('class StoreReceiptRequest(BaseModel):','''class StoreUnitScan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    system_code: str=Field(strict=True,min_length=1,max_length=40)
    profile_code: str=Field(strict=True,min_length=1,max_length=60)
    code: str=Field(strict=True,min_length=1,max_length=4000)

class StoreReceiptRequest(BaseModel):
    scans: list[StoreUnitScan]=Field(default_factory=list,max_length=20000)''')
s=s.replace('exclude={"operation_id","load_operation_id","store_address","observations",','exclude={"scans","operation_id","load_operation_id","store_address","observations",')
s=s.replace('    if body.observations:', '    if body.scans:\n        metadata["scans"]=[scan.model_dump() for scan in body.scans]\n    if body.observations:',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py");s=p.read_text(encoding="utf-8")
s=s.replace('        return self.post("STORE_RECEIPT",operation_id,','''        metadata=dict(metadata)
        scans=metadata.pop("scans",None)
        if scans:
            from ...inventory.public import normalize_unit_scan_codes
            try:
                metadata["unit_scans"]=normalize_unit_scan_codes(scans)
            except ValueError as exc:
                raise StoreReceiptError("STORE_MARK_SCAN_INVALID",str(exc),422,operation_id) from exc
        return self.post("STORE_RECEIPT",operation_id,''',1)
out[str(p)]=s
# Reuse shared identity boundary in previous interwarehouse adapter too.
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
start=s.index('            from ..domain.mark_identity import canonical_mark',s.index('    def receive_action'))
end=s.index('            except ValueError',start)
s=s[:start]+'''            from ..public import normalize_unit_scan_codes
            from fastapi import HTTPException
            try:
                metadata["unit_scans"] = normalize_unit_scan_codes(scans)
'''+s[end:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
