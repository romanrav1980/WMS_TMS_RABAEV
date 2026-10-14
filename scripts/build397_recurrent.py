from pathlib import Path
import json
out={}
t=Path("scripts/receive390_initial.py").read_text(encoding="utf-8").replace("390","396")
t=t.replace("UNIT_ID='1'","UNIT_ID='3'").replace('ctx["units"][0]["codes"]','next(u for u in ctx["units"]if u["unit_id"]=="3")["codes"]').replace('result["short_quantity"]=="2"','result["short_quantity"]=="1"')
out["scripts/receive396_initial.py"]=t
t=Path("scripts/case391_whole_found.py").read_text(encoding="utf-8").replace("390","396").replace("391","397")
t=t.replace('quantity="2"','quantity="1"').replace("assert len(lost)==2","assert len(lost)==1")
t=t.replace('q.fetchone()==(2,2)','q.fetchone()==(1,1)')
out["scripts/case397_recurrent_found.py"]=t
print(json.dumps(out))
