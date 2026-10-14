from pathlib import Path
import json
s=Path("scripts/ni052_fullpal_current_slot_case.py").read_text(encoding="utf-8").replace("select STATUS from RRL_WAREHOUSE_TASK_SYNC","select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC").replace("SOURCE_CELL_SLOT_ID","CELL_SLOT_ID")
out={"scripts/ni052_fullpal_current_slot_case.py":s}
p=Path("scripts/build222_case.py");out[str(p)]=p.read_text(encoding="utf-8").replace("select STATUS from RRL_WAREHOUSE_TASK_SYNC","select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC").replace("SOURCE_CELL_SLOT_ID","CELL_SLOT_ID")
prefix=s[:s.index(' admin_api=')]
tail=s[s.index(' q.execute("select c.TASK_ID,c.STATUS'):];tail=tail.replace('unload["operation_id"]','winner')
setup=""" load_id="FULL222.LOAD:"+tag
 q.execute("select u.OPERATION_ID,c.CELL_SLOT_ID,sl.SLOT_CODE from RRL_TT_UNLOAD_FACT u join RRL_RECEIPT_SLOT_CLAIM c on c.UID_PALLET=u.ROOT_UID and c.CELL=u.CELL_CODE join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=c.CELL_SLOT_ID where u.LOAD_OPERATION_ID=:p",p=load_id);winner,slot,code=q.fetchone()
"""
out["scripts/resume222_case.py"]=prefix+setup+tail
print(json.dumps(out,ensure_ascii=True))
