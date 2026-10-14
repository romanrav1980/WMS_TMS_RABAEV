from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_vehicle_floor_rule/"
p=Path(root+"003_plan_rule.sql");s=p.read_text(encoding="utf-8")
s=s.replace("   result.put('floor_capacity',floor_value);\n","",1)
point="  result.put('validation_status',case";assert point in s;s=s.replace(point,"  result.put('floor_capacity',floor_value);\n"+point,1);f[str(p)]=s
f[root+"apply_result_correction.sql"]="@@003_plan_rule.sql\nalter package RRL_TRANSPORT_PLAN_API compile body;\n/\n"
p=Path("scripts/build1186_vehicle_floor_rule.py");s=p.read_text(encoding="utf-8")
s=s.replace('point="  result.put(\'validation_status\'"','point="  result.put(\'validation_status\',case"')
f[str(p)]=s
print(json.dumps(f))
