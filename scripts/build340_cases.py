from pathlib import Path
import json
out={};old=Path("scripts/source311_marked_case.py").read_text(encoding="utf-8")
for num in["340","341"]:
 s=old.replace("311",num)
 if num=="341":
  s=s.replace('[("CRPT","TOBACCO"),("EGAIS","ALCOHOL")]','[("CRPT","TOBACCO")]')
  marker=' q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER")'
  s=s.replace(marker,' for unit in units:unit["codes"]=[code for code in unit["codes"]if code["system_code"]=="CRPT"]\n'+marker)
  marker='  supply=ET.Element('
  idx=s.index(marker)
  s=s[:idx]+'  scan_aggregations=[x for x in scan_aggregations if x["system_code"]=="CRPT"]\n'+s[idx:]
  start=s.index("  target=ware+50000000;");end=s.index("  now=datetime.now",start)
  s=s[:start]+"""  common=json.loads(Path("tmp/context340.json").read_text(encoding="utf-8"))
  target=common["target_warehouse"];inbound=common["inbound"];outbound=common["outbound"];target_trip=common["target_trip"]
"""+s[end:]
 out["scripts/source"+num+"_marked_case.py"]=s
s=Path("scripts/prepare336_consolidation.py").read_text(encoding="utf-8").replace('"334","335"','"340","341"').replace("336","342");out["scripts/prepare342_consolidation.py"]=s
s=Path("scripts/case337_consolidated_load.py").read_text(encoding="utf-8").replace("context336.json","context342.json").replace("337","343");out["scripts/case343_consolidated_load.py"]=s
s=Path("scripts/deliver338_consolidated.py").read_text(encoding="utf-8").replace("context336.json","context342.json").replace("338","344");out["scripts/deliver344_consolidated.py"]=s
print(json.dumps(out))
