from pathlib import Path
import json
m=json.loads(Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json").read_text(encoding="utf-8"))
for x in m["increments"]:print(json.dumps({k:x.get(k)for k in["id","title","status","remainingScope"]},ensure_ascii=True))
