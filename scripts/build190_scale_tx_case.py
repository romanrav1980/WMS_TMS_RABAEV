from pathlib import Path
import json
t=Path("scripts/ni042_warehouse_scale_net_case.py").read_text(encoding="utf-8").replace("189","190")
t=t.replace("import sys,json,re","import sys,json,re\nfrom concurrent.futures import ThreadPoolExecutor")
anchor='  result=request(f"/tasks/{case}/lines/{line}/weigh-line",body)'
assert t.count(anchor)==1
section='''  metadata={"fact_qty":"9.6","scan_cell":cell,"scan_container":carrier,"scan_product":article,
      "offline_event_id":None,"warehouse_scale_capture":capture["capture_key"],"weighed_confirmation":body}
  wire=json.dumps({"contract_version":2,"operation_id":operation,"command_type":"CASE_PICK_CONFIRM",
      "actor":"admin","source":{"case_task_id":case,"case_line_id":line},"lines":[],"units":[],"metadata":metadata})
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,wire)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);assert out.getvalue() is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select STOCK_OPERATION_ID from RRL_WH_SCALE_USE where CAPTURE_KEY=:p_key",p_key=capture["capture_key"]);assert q.fetchone()==(operation,)
   q.execute("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert str(q.fetchone()[0])=="9.6"
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_WH_SCALE_USE where CAPTURE_KEY=:p_key",p_key=capture["capture_key"]);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=operation);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=operation);assert q.fetchone()==(0,)
  q.execute("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()==(0,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(20,10)
  print("PASS190 outer rollback removes USE/operation/events/CASE quantity and restores P/H",flush=True)
  contenders=[body,{**body,"operation_id":operation+":B"}]
  def race(payload):
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    answer=client.post(base+f"/tasks/{case}/lines/{line}/weigh-line",json=payload)
    return payload,answer.status_code,answer.json()
  with ThreadPoolExecutor(max_workers=2)as pool:answers=list(pool.map(race,contenders))
  assert sorted(a[1]for a in answers)==[200,409],answers
  body,status,result=next(a for a in answers if a[1]==200);operation=body["operation_id"]
  print("PASS190 different-operation concurrent capture exactly one winner; loser409",operation,flush=True)
'''
t=t.replace(anchor,section)
print(json.dumps({"scripts/ni042_warehouse_scale_tx_case.py":t},ensure_ascii=True))
