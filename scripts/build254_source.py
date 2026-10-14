from pathlib import Path
import json
s=Path("scripts/ni053_marked_disposition_source.py").read_text(encoding="utf-8")
needle='  completed=post("TASK_COMPLETE",'
assert s.count(needle)==1
prefix="""  from app.services.warehouse_task_service import WarehouseTaskService
  from app.schemas import WarehouseTaskStatusRequest
  WarehouseTaskService(OracleGateway()).start_task(task,WarehouseTaskStatusRequest(updated_by="admin"))
  q.execute("select STATUS,STARTED_AT_INSTANT,FINISHED_AT_INSTANT from RRL_WAREHOUSE_TASK where TASK_ID=:tid",tid=task)
  state,started,finished=q.fetchone();assert state=="IN_PROGRESS"and started is not None and finished is None
  rollback_cmd={"contract_version":2,"operation_id":"TASK254.COMPLETE:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst}}
  clock_out=q.var(oracledb.DB_TYPE_CLOB)
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(rollback_cmd),"admin",clock_out,None])
  if clock_out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[clock_out])
  q.execute("select FINISHED_AT_INSTANT from RRL_WAREHOUSE_TASK where TASK_ID=:tid",tid=task);assert q.fetchone()[0]is not None
  conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS,STARTED_AT_INSTANT,FINISHED_AT_INSTANT from RRL_WAREHOUSE_TASK where TASK_ID=:tid",tid=task)
  assert q.fetchone()==(state,started,None)
"""
s=s.replace(needle,prefix+needle)
old='{"task_id":task})\n  preview=FullPalletShipment'
new='{"task_id":task},"TASK254.COMPLETE:"+tag)\n  q.execute("select FINISHED_AT_INSTANT from RRL_WAREHOUSE_TASK where TASK_ID=:tid",tid=task);done_clock=q.fetchone()[0];assert done_clock is not None\n  assert post("TASK_COMPLETE",rollback_cmd["metadata"],{"task_id":task},"TASK254.COMPLETE:"+tag)==completed\n  q.execute("select FINISHED_AT_INSTANT from RRL_WAREHOUSE_TASK where TASK_ID=:tid",tid=task);assert q.fetchone()[0]==done_clock\n  preview=FullPalletShipment'
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("loading.preview_single(st_uid)","loading.preview_single(st_uid,'admin')")
s=s.replace('SOURCE230_JSON:','SOURCE254_JSON:').replace('"tag":tag,"uid":lot','"task_id":task,"tag":tag,"uid":lot')
print(json.dumps({"scripts/source254_time.py":s},ensure_ascii=True))
