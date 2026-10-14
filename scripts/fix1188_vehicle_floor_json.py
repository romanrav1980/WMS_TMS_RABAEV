from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_vehicle_floor_rule/"
p=Path(root+"002_profile_body.sql");s=p.read_text(encoding="utf-8")
for name,index in(("variants","i"),("counts","j"),("limits","k")):
 old=f"{name}.get_object({index})";assert old in s;s=s.replace(old,f"treat({name}.get({index}) as json_object_t)")
f[str(p)]=s
f[root+"apply_json_correction.sql"]="@@002_profile_body.sql\nalter package RRL_TRANSPORT_PLAN_RULES compile body;\n/\nalter package RRL_TRANSPORT_PLAN_API compile body;\n/\nalter package RRL_STOCK_LOAD_THERMAL compile body;\n/\n"
p=Path("scripts/build1186_vehicle_floor_rule.py");s=p.read_text(encoding="utf-8")
for name,index in(("variants","i"),("counts","j"),("limits","k")):
 s=s.replace(f"{name}.get_object({index})",f"treat({name}.get({index}) as json_object_t)")
f[str(p)]=s
print(json.dumps(f))
