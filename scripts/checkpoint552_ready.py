import hashlib,json
from pathlib import Path
folder=Path("db/migrations/2026-10-12_ni063_damage_custody")
checkpoint=json.loads((folder/"checkpoint.json").read_text(encoding="utf-8"))
checkpoint["prepared_sha256"]={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.glob("*.sql")}
checkpoint["install_order"]="guards first, LOSS/TARE before RESOLVE creates first new origins; no reconstruction of existing balances"
out={str(folder/"checkpoint.json"):json.dumps(checkpoint,indent=2)+"\n"}
p=Path("wiki/index.md");out[str(p)]="- [NI06.3: происхождение повреждённой тары](database/retailcase_ni063_damage_custody_20261012.md):552 подготовлена, сохранены текущие native источники; связь DAMAGE → OFFER/ACCEPT → складское списание в прежнем ядре.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-12 checkpoint552 prepared: additive provenance for new damaged tare, existing physical root commands retain all quantity effects; source manifest/paired rollback/native installation order saved. Not applied or accepted yet.\n"
print(json.dumps(out))
