from pathlib import Path
import json
out={}
s=Path("scripts/source292_marked_case.py").read_text(encoding="utf-8").replace("292","305")
s=s.replace('if Path("tmp/context305.json").exists():','if Path("tmp/context305.json").exists()or Path("tmp/source305_progress.json").exists():',1)
s=s.replace('select min(TRANSPORTTYPE) from RRL_TRANSPORT_TYPE',"select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'",1)
out["scripts/source305_marked_case.py"]=s
print(json.dumps(out))
