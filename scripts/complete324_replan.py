from pathlib import Path
import json
s=Path("scripts/case317_hu_placement.py").read_text(encoding="utf-8")
s=s.replace('p=Path("tmp/context317.json");receipt=json.loads(Path("tmp/context314_received.json").read_text(encoding="utf-8"));source=receipt["source"];saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{}','p=Path("tmp/context324.json");receipt=json.loads(Path("tmp/context322_received.json").read_text(encoding="utf-8"));source=receipt["source"];saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{};retained=json.loads(Path("tmp/context323.json").read_text(encoding="utf-8"));saved.setdefault("plan",retained["replan"])')
s=s.replace("IW317.PLAN:","IW324.PLAN:").replace("IW317.COMPLETE:","IW324.COMPLETE:").replace("PASS317","PASS324")
print(json.dumps({"scripts/case324_hu_placement.py":s}))
