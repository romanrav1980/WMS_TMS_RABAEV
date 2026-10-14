from pathlib import Path
import hashlib,json
folder=Path("db/migrations/2026-10-11_ni042_weight_box_dimensions")
print(json.dumps({str(folder/"checkpoint.json"):json.dumps({"migration_id":"2026-10-11-183-physical-box-dimensions","sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.glob("*.sql")},"recovery":"Four additive nullable metadata columns; guarded paired rollback refuses history removal; no database copy"},indent=2)},ensure_ascii=True))
