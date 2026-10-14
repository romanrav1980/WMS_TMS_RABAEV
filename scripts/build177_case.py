import json
from pathlib import Path
s=Path("scripts/ni041_case_relocation_existing_case.py").read_text(encoding="utf-8")
s=s.replace('"""175 fresh native CASE12+8, unpack and same-cell CASE slot relocation; no fake terminal cleanup."""','"""177 real slotted CASE packing: reuse175 source flow, retain native tare and stock; no fake terminal cleanup."""')
pos=s.index('  move_case={"target_cell":case_stage')
section="""  parent_version=int(hu_tree()["nodes"][0]["version"])
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=ct);child_version=int(q.fetchone()[0])
  repack={"child_case_task_id":ct,"retained_tare_booking_operation_id":"QA175.TARE.BOOK:"+str(ct),"expected_version":parent_version,"expected_child_version":child_version,"scan_container":parent,"scan_child":carrier,"scan_cell":hu_dst,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[2][1],"measurements":measures(parent_version,30),"reason":"Owned177 pack whole CASE without returning its tare"}
  op177="HU.REPACK177:"+tag;url177="http://127.0.0.1:8088/api/warehouse-hus/repack-case-slot"
  body177={"operation_id":op177,"identifier":parent,**repack}
  with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
   bad=client.post(url177,json={**body177,"operation_id":op177+".TOO_HEAVY","measurements":measures(parent_version,110)})
   assert bad.status_code==409,(bad.status_code,bad.text[:1800])
  assert hu_tree()["nodes"][0]["version"]==parent_version
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(child_version,)
  q.execute("select count(*),sum(HU_GROSS_WEIGHT_KG)from RRL_RECEIPT_SLOT_CLAIM where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(2,30)
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=op177+".TOO_HEAVY");assert q.fetchone()==(0,)
  command={"contract_version":2,"operation_id":op177+".ROLLBACK","command_type":"HU_REPACK_SLOT","actor":"admin","source":{"uid":parent},"lines":[],"units":[],"metadata":repack}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(1,)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  assert hu_tree()["nodes"][0]["version"]==parent_version
  q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(2,)
  def repack_call():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    response=client.post(url177,json=body177);assert response.status_code==200,(response.status_code,response.text[:1800]);return response.json()
  with ThreadPoolExecutor(max_workers=2)as pool:replies177=list(pool.map(lambda _:repack_call(),range(2)))
  assert replies177[0]==replies177[1]and replies177[0]["quantity_unchanged"]and replies177[0]["tare_assets_preserved"]
  q.execute("select count(*),sum(HU_GROSS_WEIGHT_KG)from RRL_RECEIPT_SLOT_CLAIM where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(1,30)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(20,20)
  q.execute("select count(*)from RRL_TARE_BOOK where OPERATION_ID in(:p_first,:p_second)and STATUS='HELD'",p_first=bookings[0],p_second=bookings[1]);assert q.fetchone()==(2,)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=op177);assert q.fetchone()==(0,)
  from app.services.warehouse_task_domain_sync_service import WarehouseTaskDomainSyncService
  sync=WarehouseTaskDomainSyncService(OracleGateway())
  assert sync.retry_sync(int(replies177[0]["task_id"]),"admin")["sync_status"]=="SYNCED"
  with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
   assert client.post(url177,json={**body177,"reason":"Changed saved packing request"}).status_code==409
  # Existing unpack restores a separate physical slot, so the remaining source cleanup is unchanged.
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=ct);child_version=int(q.fetchone()[0])
  parent_version=int(hu_tree()["nodes"][0]["version"])
  post("HU_UNPACK",{"child_case_task_id":ct,"expected_version":parent_version,"expected_child_version":child_version,"scan_container":parent,"scan_child":carrier,"scan_cell":hu_dst,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Owned177 unpack whole nested CASE again","parent_measurements":measures(parent_version,15),"child_measurements":measures(child_version,15)},{"uid":parent},"HU.REPACK177.UNPACK:"+tag)
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=ct);version=int(q.fetchone()[0])-1
  print("PASS177 real CASE12/parent8 two occupied slots -> one30kg slot/P20H20/HELDtare2; late capacity refusal + rollback restore both sources; concurrent exact receipt once; native sync retry; unpack reversal",wave,op177,flush=True)
"""
s=s[:pos]+section+s[pos:]
print(json.dumps({"scripts/ni041_slot_repack_existing_case.py":s}))
