import json
from pathlib import Path
out={}
for old,new in ((404,669),(405,670)):
 s=Path("scripts/source"+str(old)+"_group.py").read_text(encoding="utf-8").replace(str(old),str(new))
 if old==405:s=s.replace("context404","context669")
 # Current warehouse group shipping is a system cell; retain original BASE/identity writers.
 s=s.replace("revision=int(q.callfunc", "meta(\"update RRL_CELLS set IS_SYSTEM=1 where CELL=:cell\",cell=shipcell)\n revision=int(q.callfunc")
 out["scripts/source"+str(new)+"_group_agg.py"]=s
out["scripts/prepare671_group_agg.py"]=Path("scripts/prepare406_group.py").read_text(encoding="utf-8").replace("406","671").replace("404","669").replace("405","670")
out["scripts/plan672_group_agg.py"]=Path("scripts/case407_group_plan.py").read_text(encoding="utf-8").replace("407","672").replace("406","671")
print(json.dumps(out))
