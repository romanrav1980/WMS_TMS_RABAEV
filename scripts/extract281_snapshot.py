from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/infrastructure/road_leg_estimate.py");s=p.read_text(encoding="utf-8")
start=s.index("            out=cur.var");end=s.index("    except oracledb.DatabaseError",start)
body=s[start:end];body="\n".join(line[8:]if line.startswith("        ")else line for line in body.splitlines())
s=s[:start]+"            return read_snapshot(cur,trip,depot,max_age,actor)\n"+s[end:]
s+="\ndef read_snapshot(cur: Any,trip: int,depot: str,max_age: int,actor: str) -> dict:\n"+body+"\n"
print(json.dumps({str(p):s},ensure_ascii=True))
