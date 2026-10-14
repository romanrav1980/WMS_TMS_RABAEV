import json
from pathlib import Path
out={}
for src,dst in [("source311_marked_case.py","source464_marked_case.py"),("case311_aggregate_receive.py","case464_aggregate_receive.py")]:
 s=(Path("scripts")/src).read_text(encoding="utf-8-sig").replace("311","464")
 out[str(Path("scripts")/dst)]=s
print(json.dumps(out))
