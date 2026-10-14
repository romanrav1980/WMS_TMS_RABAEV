from pathlib import Path
import json
p=Path("scripts/ni042_direct_receiving_case.py");s=p.read_text(encoding="utf-8")
anchor='  picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="DIRECT199.LAUNCH:"+tag))'
before='''  wire=StockCommand(operation_id="DIRECT199.LAUNCH:"+tag,command_type="WAVE_LAUNCH",actor="admin",source={"wave_id":wave},metadata={},lines=()).canonical_json()
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,wire)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="CANCELLED"
   q.execute("select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()[0]==20
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="PLANNED"
  q.execute("select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()[0]==0
  print("PASS199 outer rollback restores original placement and source HARD0",flush=True)
'''
assert anchor in s;s=s.replace(anchor,before+anchor)
# Retain the direct native diagnostic only on a real HTTP failure.
a='''   try: CasePickService().confirm_line(int(case),int(line),CasePickLineConfirmRequest(**payload,actor="admin"))
   except HTTPException as exc: print("Native199 reason",str(exc.__cause__.__cause__)[:2200],flush=True);raise
   picked=call("POST",path,payload);assert call("POST",path,payload)==picked'''
b='''   try:picked=call("POST",path,payload)
   except AssertionError:
    try:CasePickService().confirm_line(int(case),int(line),CasePickLineConfirmRequest(**payload,actor="admin"))
    except HTTPException as exc:print("Native199 reason",str(exc.__cause__.__cause__)[:2200],flush=True)
    raise
   assert call("POST",path,payload)==picked'''
assert a in s;s=s.replace(a,b)
print(json.dumps({str(p):s},ensure_ascii=True))
