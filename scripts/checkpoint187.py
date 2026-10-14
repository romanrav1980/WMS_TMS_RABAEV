from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-11_ni042_warehouse_scale")
print(json.dumps({str(f/"checkpoint.json"):json.dumps({"migration_id":"2026-10-11-187-warehouse-scale-archive","sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")},"recovery":"Additive empty warehouse scale metadata only; history-protected rollback; no DB copy"},indent=2)},ensure_ascii=True))
