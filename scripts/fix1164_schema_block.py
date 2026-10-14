from pathlib import Path
import json,hashlib
p=Path("db/migrations/2026-10-14_ni052_loading_temperature/001_schema.sql")
s=p.read_text(encoding="utf-8").strip().removesuffix("/").strip()
s="begin execute immediate q'["+s+"]';end;\n/\n"
f={str(p):s}
p=Path("db/migrations/2026-10-14_ni052_loading_temperature/checkpoint.json");d=json.loads(p.read_text(encoding="utf-8"));d["initial_apply"]="OracleApply parsed bare multiline CREATE TABLE as one line, ORA-00922 before any completed statement. Fixed to existing repository PL/SQL execute immediate schema pattern."
d["prepared_sha256"][next(iter(f))]=hashlib.sha256(s.encode("utf-8")).hexdigest();f[str(p)]=json.dumps(d,indent=2)
print(json.dumps(f))
