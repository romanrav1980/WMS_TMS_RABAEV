from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-11_ni052_unload");out={}
for p in("wiki-raw/wms_admin_ui_reference/transport-loading.js","wiki-raw/wms_admin_ui_reference/transport-loading.html"):
 out[str(f/("000_before_"+Path(p).name))]=Path(p).read_text(encoding="utf-8")
out[str(f/"ui_checkpoint.json")]=json.dumps({"sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"note":"Fresh UI source before unloading extension. Initial212 checkpoint covers actual root/guards/core contracts and transport contracts/routes/repository. Main/public/composition glue undo reconstructed from recorded narrow edits, not claimed byte-exact original capture."},indent=2)
print(json.dumps(out,ensure_ascii=True))
