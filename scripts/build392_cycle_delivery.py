from pathlib import Path
import json
out={}
t=Path("scripts/place371.py").read_text(encoding="utf-8").replace("368","390").replace("371","392")
t=t.replace("assert qty==1","assert qty in(1,2)").replace('fact_qty="1"','fact_qty=str(int(qty))').replace('q.fetchone()==(1,0)','q.fetchone()==(qty,0)').replace('q.fetchone()==(1,1)','q.fetchone()==(int(qty),qty)')
out["scripts/place392_cycle.py"]=t
t=Path("scripts/prepare372_recovery_consolidation.py").read_text(encoding="utf-8").replace("368","390").replace("372","392")
t=t.replace("range(3)","range(2)").replace("set PALLETS=3","set PALLETS=2").replace("assert len(ids)==1","assert len(ids)==(1 if index==0 else 2)").replace('["leaf_count"]==3','["leaf_count"]==2')
out["scripts/prepare392_cycle.py"]=t
t=Path("scripts/case373_recovery_load.py").read_text(encoding="utf-8").replace("372","392").replace("373","393")
t=t.replace("q.fetchone()==(2,2)","q.fetchone()==(1,2)")
t=t.replace("q.fetchone()==(1,0)","q.fetchone()==(int(part['onward']['quantity']),0)")
t=t.replace("q.fetchone()[0]==3","q.fetchone()[0]==2")
out["scripts/load393_cycle.py"]=t
t=Path("scripts/deliver374_recovery_consolidation.py").read_text(encoding="utf-8").replace("372","392").replace("374","393")
out["scripts/deliver393_cycle.py"]=t
print(json.dumps(out))
