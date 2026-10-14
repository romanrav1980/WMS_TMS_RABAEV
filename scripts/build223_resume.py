from pathlib import Path
import json
s=Path("scripts/ni052_single_load_slot_release_case.py").read_text(encoding="utf-8");old='proof=json.loads(q.fetchone()[0].read());'
new='value=q.fetchone()[0];proof=value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,"read")else value);'
assert old in s;s=s.replace(old,new,1);out={"scripts/ni052_single_load_slot_release_case.py":s}
p=Path("scripts/build223_case.py");out[str(p)]=p.read_text(encoding="utf-8").replace(old,new,1)
prefix=s[:s.index(' admin_api=')]
tail=s[s.index(' q.execute("select RESOLVED_PLAN_JSON'):];setup=""" place_task=949;slot=221
 q.execute("select OPERATION_ID from RRL_STOCK_OPERATION where STATE='APPLIED'and COMMAND_TYPE='LOAD_SHIPMENT'and OPERATION_ID like 'FULL223.LOAD:6ac14257b5%'");rows=q.fetchall();assert len(rows)==1;load_id=rows[0][0]
 q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t",t=place_task);assert q.fetchone()[0]==0
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=place_task);assert q.fetchone()[0]=="DONE"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=load_id);assert q.fetchone()[0]==-3
"""
out["scripts/resume223_case.py"]=prefix+setup+tail
print(json.dumps(out,ensure_ascii=True))
