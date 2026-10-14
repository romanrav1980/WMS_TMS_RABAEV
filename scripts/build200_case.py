from pathlib import Path
import json
s=Path("scripts/ni042_direct_receiving_case.py").read_text(encoding="utf-8").replace("199","200")
s=s.replace('zip(customers,(12,8))','zip(customers,(12,))')
s=s.replace('assert q.fetchone()[0]==20\n  finally','assert q.fetchone()[0]==12\n  finally')
s=s.replace('assert sorted(r[4]for r in rows)==[8,12]','assert sorted(r[4]for r in rows)==[12]')
s=s.replace('assert q.fetchone()==(0,0)\n  q.execute("select sum(PICKED_QTY)','assert q.fetchone()==(8,0)\n  q.execute("select sum(PICKED_QTY)')
s=s.replace('assert q.fetchone()[0]==20\n  print("PASS200','assert q.fetchone()[0]==12\n  print("PASS200')
anchor='  post("WAVE_PICK_RELEASE",{"wave_id":wave},{})'
before='''  replan={"operation_id":"DIRECT200.REPLAN:"+tag,"scanned_pallet":sscc,"scanned_from_cell":receive,"reason":"Place current free physical remainder after completed direct order"}
  refused=api.post(base+f"/api/receiving/putaway/{task}/replan",json=replan)
  assert refused.status_code==409,(refused.status_code,refused.text)
  q.execute("select STATUS,QTY from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()==("CANCELLED",20)
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
anchor='  print("PASS200 actual SAP'
idx=s.index(anchor)
s=s[:idx]+'''  replanned=call("POST",f"/api/receiving/putaway/{task}/replan",replan)
  assert replanned["original_received_base_quantity"]=="20"and replanned["current_base_quantity"]=="8"and replanned["current_task_quantity"]=="8",replanned
  retry=call("POST",f"/api/receiving/putaway/{task}/replan",replan);assert retry["idempotent"]and retry["current_task_quantity"]=="8"
  q.execute("select STATUS,QTY,TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);status,quantity,target=q.fetchone()
  assert status=="PLANNED"and quantity==8 and target==storage
  from app.modules.inventory.infrastructure.receiving import Receiving
  completed=Receiving(OracleGateway()).complete(task,{"fact_qty":"8","scanned_pallet":sscc,"scanned_from_cell":receive,"scanned_to_cell":target,"operation_id":"DIRECT200.PUT:"+tag},"admin")
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=storage);assert q.fetchone()==(8,0)
  q.execute("select POSTED_BASE_QTY from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p_uid",p_uid=sscc);assert q.fetchone()[0]==20
  q.execute("select PAYLOAD_JSON from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:p_id",p_id="PUTAWAY:"+str(task));outgoing=read_oracle_json(q.fetchone()[0]);assert outgoing["base_quantity"]=="8",outgoing
  print("PASS200 actual SAP20/direct order12/free original-source8/replan before pending allocation409/current physical/version/native handoff proof/replay/original admission20 retained/existing TASK_COMPLETE storage8/outbox8",article,task,flush=True)
''' +s[idx:]
# Completed original putaway cannot be cancelled: keep its historical DONE fact.
s=s.replace('   Receiving(OracleGateway()).cancel(task,"Owned200 fixture cleanup","admin")','   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task)\n   if q.fetchone()[0]!="DONE":Receiving(OracleGateway()).cancel(task,"Owned200 fixture cleanup","admin")')
print(json.dumps({"scripts/ni042_direct_residual_case.py":s},ensure_ascii=True))
