import json,hashlib
from pathlib import Path
folder=Path("db/migrations/2026-10-12_ni071_vehicle_source");m=json.loads((folder/"checkpoint.json").read_text(encoding="utf-8"))
m["prepared_sha256"]={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.glob("*.sql")}
m["install_order"]="schema/profile/source APIs and guards first, patch original DEPART last; no historical departure inference"
out={str(folder/"checkpoint.json"):json.dumps(m,indent=2)+"\n"}
p=Path("wiki/index.md");out[str(p)]="- [NI07.1: класс автомобиля фиксируется на выезде](database/retailcase_ni071_vehicle_source_20261012.md):559/560 подготовлены, native/API/profile snapshots; применение ещё не выполнено.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-12 checkpoint559/560 prepared: saved actual DEPART source and fleet columns, versioned dimension/class native config and original departure source/one instant, modular API/source manifest/paired rollback. Not applied yet.\n"
print(json.dumps(out))
