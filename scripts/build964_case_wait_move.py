from pathlib import Path
import json
old=Path("scripts/finish962_case_wait.py").read_text(encoding="utf-8")
head=old[:old.index(" try:\n  def planning():")]
head=head.replace('context["stage"]=="DEFERRED"','context["stage"]=="PLANNED"')
body=old[old.index('  task=int(planned["tasks"]'):];body=' try:\n  planned=context["plan_result"]\n'+body
needle='  req=WarehouseTaskStatusRequest('
pos=body.index(needle)
trial="""  native={"contract_version":2,"operation_id":"ROLLBACK955:"+tag,"command_type":"CASE_CARRIER_MOVE","actor":"admin","source":{"case_task_id":int(ct)},"lines":[],"units":[],"metadata":command}
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(native),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   trial_move=read_oracle_json(out.getvalue());assert trial_move["status"]=="DONE"
   q.execute("select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",1)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("PLANNED",None)
  q.execute("select CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));assert q.fetchone()==(origin,version)
  context["native_move_rollback"]=True;save_context()
"""
body=body[:pos]+trial+body[pos:]
print(json.dumps({"scripts/move964_case_wait.py":head+body},ensure_ascii=True))
