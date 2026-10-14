from pathlib import Path
p=Path("scripts/return394_cycle.py");t=p.read_text(encoding="utf-8")
needle=' if "sap"not in saved:'
insert=''' q.execute("select LINE_NO from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op and LOT_UID=:lot and ACCEPTED_BASE_QTY=2",op=source,lot=origin["lot"]);line_no=int(q.fetchone()[0])
 approval={"operation_id":"REUSE394.APPROVE:"+tag,"line_no":line_no,"quantity":"2","disposition":"REUSE","reason":"Own original complete marked BOX3 returned","decision_reference":"DEV394:"+tag,"complete_good_box":True,"unit_keys":keys}
 if "approval"not in saved:saved["approval"]=call(admin,"POST","/api/delivery/store-returns/"+source+"/approve",approval);save()
'''
t=t.replace(needle,insert+needle,1)
# Resume the already started native task; do not create or reassign another one.
a=t.index('  if "done"not in saved:');b=t.index('  assert call(admin,"POST",f"/api/warehouse-tasks/{task}/complete"',a)
t=t[:a]+'''  if "done"not in saved:
   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:task_id",task_id=task);task_status=q.fetchone()[0]
   if task_status=="PLANNED":call(admin,"POST",f"/api/warehouse-tasks/{task}/assign",{"assigned_to":"admin"});task_status="ASSIGNED"
   if task_status=="ASSIGNED":call(admin,"POST",f"/api/warehouse-tasks/{task}/start",{})
   completion={"operation_id":"REUSE394.DONE:"+tag,"scanned_pallet":uid,"scanned_from_cell":cells[2],"scanned_to_cell":target,"fact_qty":"2"}
   saved["done"]=call(admin,"POST",f"/api/warehouse-tasks/{task}/complete",completion);saved["done_body"]=completion;save()
'''+t[b:]
import json
print(json.dumps({p.as_posix():t}))
