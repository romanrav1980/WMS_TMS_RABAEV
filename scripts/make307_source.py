from pathlib import Path
import json
out={}
s=Path("scripts/source305_marked_case.py").read_text(encoding="utf-8").replace("305","307")
out["scripts/source307_marked_case.py"]=s
s=Path("scripts/receive305_initial.py").read_text(encoding="utf-8").replace("305","307")
out["scripts/receive307_initial.py"]=s
print(json.dumps(out))
