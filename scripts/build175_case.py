import json
from pathlib import Path
s=Path("scripts/ni041_case_slot_case.py").read_text(encoding="utf-8")
s=s.replace('"""Actual full-pallet move -> existing ST binding -> pinned shipment; clean only own P/H through root."""','"""175 fresh native CASE12+8, unpack and same-cell CASE slot relocation; no fake terminal cleanup."""')
s=s.replace("import json,sys","import json,sys,httpx\nfrom concurrent.futures import ThreadPoolExecutor")
s=s.replace("for index in range(2):","for index in range(3):")
anchor='  move_case={"target_cell":case_stage'
pos=s.index(anchor)
section="""  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=ct);relversion=int(q.fetchone()[0])
  relocation={"case_task_id":ct,"expected_version":relversion,"target_slot_id":slots[2][0],"scan_container":carrier,"scan_cell":hu_dst,"scan_from_slot":slots[1][1],"scan_to_slot":slots[2][1],"measurements":measures(relversion,15),"reason":"Owned175 physical CASE slot relocation"}
  op175="CASE.RELOCATE175:"+tag
  command={"contract_version":2,"operation_id":op175+".ROLLBACK","command_type":"HU_RELOCATE_SLOT","actor":"admin","source":{"uid":"CASE:"+str(ct)},"lines":[],"units":[],"metadata":relocation}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(slots[2][0],)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select CELL_SLOT_ID,HU_COMPOSITION_VERSION from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(slots[1][0],relversion)
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=command["operation_id"]);assert q.fetchone()==(0,)
  body175={"operation_id":op175,"identifier":"CASE:"+str(ct),**relocation}
  url175="http://127.0.0.1:8088/api/warehouse-hus/relocate-slot"
  with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
   denied=client.post(url175,json={**body175,"operation_id":op175+".BADSCAN","scan_from_slot":"Wrong175"})
   assert denied.status_code==409,(denied.status_code,denied.text[:1800])
  def relocate():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    response=client.post(url175,json=body175);assert response.status_code==200,(response.status_code,response.text[:1800]);return response.json()
  with ThreadPoolExecutor(max_workers=2)as pool:replies=list(pool.map(lambda _:relocate(),range(2)))
  assert replies[0]==replies[1]and replies[0]["quantity_unchanged"]
  q.execute("select CELL_SLOT_ID,HU_COMPOSITION_VERSION from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(slots[2][0],relversion+1)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(20,20)
  q.execute("select count(*),sum(HU_GROSS_WEIGHT_KG)from RRL_RECEIPT_SLOT_CLAIM where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(2,30)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=op175);assert q.fetchone()==(0,)
  with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
   assert client.post(url175,json={**body175,"reason":"Other physical decision"}).status_code==409
  version=relversion
  print("PASS175 CASE12 slot1->slot2/native rollback/concurrent same receipt once/badscan409/changed409/P20H20/no quantity journal/two claims30kg",flush=True)
"""
s=s[:pos]+section+s[pos:]
s=s.replace('   meta("update RRL_PICK_WAVE set STATUS=\'DONE\' where PICK_WAVE_ID=:w",w=wave)','   print("Owned wave retained for explicit deferred decision; no fake DONE",wave,flush=True)')
s=s.replace('   meta("update RRL_WAREHOUSE_TASK set STATUS=\'CANCELLED\' where TASK_SOURCE=\'WAVE\' and SOURCE_DOC_ID=:w and STATUS not in(\'DONE\',\'CANCELLED\')",w=wave)', '   # Pending tasks remain for their existing native owner.')
s=s.replace('   meta("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS=\'CANCELLED\' where PICK_WAVE_ID=:w and STATUS not in(\'DONE\',\'CANCELLED\')",w=wave)', '   # No raw cancellation of physical tasks.')
s=s.replace('  for plan in plans:meta("update RRL_PICK_RESERVATION set RESERVATION_STATUS=\'RELEASED\' where PICK_PLAN_ID=:p and RESERVATION_STATUS=\'ACTIVE\'",p=plan)', '  # Native CASE return/reservation owner performs reservation release.')
print(json.dumps({"scripts/ni041_case_relocation_existing_case.py":s}))
