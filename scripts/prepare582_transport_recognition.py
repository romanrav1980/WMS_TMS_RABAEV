"""Checkpoint canonical sources without rewriting package text."""
import json,hashlib
from pathlib import Path
folder=Path("db/migrations/2026-10-12_ni071_transport_recognition")
checkpoint={"migration_id":"2026-10-12-582-transport-q26-recognition","status":"CHECKPOINT",
"scope":"Existing monetary run header; additive Q26 details/once-only departure claim/shared native owner.",
"authorization":"Owner requests all sprints in dedicated dev RABAEV.",
"recovery":"Paired rollback refuses committed facts; forward repair after recognition.",
"source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.glob("*.sql")}}
(folder/"checkpoint.json").write_text(json.dumps(checkpoint,indent=2)+"\n",encoding="utf-8")
print("582 canonical SQL checkpoint saved; no package transformations.")
