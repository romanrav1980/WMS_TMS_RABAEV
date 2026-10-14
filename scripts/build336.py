from pathlib import Path
import json
s=Path("scripts/prepare330_consolidation.py").read_text(encoding="utf-8").replace('"328","329"','"334","335"').replace("330","336")
s=s.replace('quantity="3",base_uom="EA"),"admin")','quantity="3",base_uom="EA",aggregation_scans=source["aggregations"]),"admin")')
s=s.replace('error_count=0,scans=[]','error_count=0,scans=[code for unit in source["units"]for code in unit["codes"]]')
s=s.replace(" try:\n  for source in sources:"," try:\n  q.execute(\"update RRL_TR_VEHICLE set PALLETS=2 where NUM=:plate\",plate=\"QL\"+sources[0][\"tag\"])\n  for source in sources:",1)
out={"scripts/prepare336_consolidation.py":s}
s=Path("scripts/case331_consolidated_load.py").read_text(encoding="utf-8").replace("context330.json","context336.json").replace("331","337")
out["scripts/case337_consolidated_load.py"]=s
s=Path("scripts/deliver332_consolidated.py").read_text(encoding="utf-8").replace("context330.json","context336.json").replace("332","338")
s=s.replace("scans=[])","scans=[dict(code,disposition=\"ACCEPTED\")for item in saved[\"sources\"]for unit in item[\"units\"]for code in unit[\"codes\"]])")
out["scripts/deliver338_consolidated.py"]=s
print(json.dumps(out))
