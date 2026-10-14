import json,hashlib
from pathlib import Path
f=Path("db/migrations/2026-10-12_ni071_vehicle_source")
v=(f/"000_before_config_fleet.sql").read_text(encoding="utf-8")
a="'sap_article_import','pick_topology_edit')";assert v.count(a)==1
v=v.replace(a,"'sap_article_import','pick_topology_edit','transport_fleet_edit')")
out={str(f/"010_config_fleet.sql"):v}
m=json.loads((f/"checkpoint.json").read_text(encoding="utf-8"));m["config_fleet_before_sha256"]=hashlib.sha256((f/"000_before_config_fleet.sql").read_bytes()).hexdigest();m["config_fleet_after_sha256"]=hashlib.sha256(v.encode()).hexdigest()
out[str(f/"checkpoint.json")]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
