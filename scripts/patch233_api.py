from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/api/return_custody_routes.py");s=p.read_text(encoding="utf-8").replace("from .store_receipt_routes import failure","from .store_receipt_routes import failure, StoreUnitScan")
s=s.replace("class CustodyCommand(BaseModel):","class CustodyCommand(BaseModel):\n    scans: list[StoreUnitScan]=Field(default_factory=list,max_length=20000)")
s=s.replace("body.model_dump(exclude=","body.model_dump(exclude_defaults=True,exclude=");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/return_custody.py");s=p.read_text(encoding="utf-8").replace("from ..contracts import StoreReceiptError","from ..contracts import StoreReceiptError\nfrom ...inventory.public import normalize_unit_scan_codes")
s=s.replace('        return self.post("STORE_RETURN_', '        metadata=dict(metadata)\n        scans=metadata.pop("scans",None)\n        if scans:metadata["unit_scans"]=normalize_unit_scan_codes(scans)\n        return self.post("STORE_RETURN_')
out[str(p)]=s
p=Path("db/migrations/2026-10-11_ni062_marked_custody/005_recompile.sql");s=p.read_text(encoding="utf-8")+"alter package RRL_STOCK_STORE_RECEIPT_READ compile body;\n/\nalter package RRL_STOCK_STORE_RECEIPT_CMD compile body;\n/\n";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
