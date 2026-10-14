from pathlib import Path
import json
out={}
s=Path("scripts/source340_marked_case.py").read_text(encoding="utf-8").replace("340","346");out["scripts/source346_marked_case.py"]=s
s=Path("scripts/source329_ordinary_case.py").read_text(encoding="utf-8").replace("329","347").replace("context328.json","context346.json");out["scripts/source347_ordinary_case.py"]=s
s=Path("scripts/prepare342_consolidation.py").read_text(encoding="utf-8").replace('"340","341"','"346","347"').replace("342","348")
s=s.replace('source["aggregations"]','source.get("aggregations",[])').replace('source["units"]','source.get("units",[])')
out["scripts/prepare348_consolidation.py"]=s
s=Path("scripts/case343_consolidated_load.py").read_text(encoding="utf-8").replace("context342.json","context348.json").replace("343","349");out["scripts/case349_consolidated_load.py"]=s
s=Path("scripts/deliver344_consolidated.py").read_text(encoding="utf-8").replace("context342.json","context348.json").replace("344","350").replace('item["units"]','item.get("units",[])')
out["scripts/deliver350_consolidated.py"]=s
print(json.dumps(out))
