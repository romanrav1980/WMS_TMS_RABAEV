from pathlib import Path
import json
t=Path("scripts/ni042_warehouse_scale_net_case.py").read_text(encoding="utf-8").replace("189","192")
t=t.replace("import sys,json,re","import sys,json,re\nfrom hashlib import sha256\nfrom concurrent.futures import ThreadPoolExecutor")
a='  print("PASS192 loose NET'
pos=t.index(a)
section='''  reported=request(f"/tasks/{case}/lines/{line}/short",{"picked_qty":"9.6","short_qty":"0.4",
    "reason_text":"Exact stable NET within configured order tolerance","offline_event_id":"WEIGHT192.REPORT:"+tag})
  short_id=int(reported["case_pick_short_id"])
  preview_response=api.get(base+f"/tasks/{case}/lines/{line}/order-weight-preview");assert preview_response.status_code==200,preview_response.text
  preview=preview_response.json();assert preview["within_tolerance"]
  approval={"operation_id":"WEIGHT192.DECIDE:"+tag,"decision":"WEIGHT_TOLERANCE","reason_text":"Accept exact9.6KG against original10KG within15 percent",
    "expected_weight_policy_version":preview["policy_version"],"expected_content_version":preview["content_version"],
    "expected_order_weight_signature":preview["order_weight_signature"]}
  denied=api.post(base+f"/shorts/{short_id}/approve",json={**approval,"operation_id":approval["operation_id"]+":STALE","expected_order_weight_signature":"0"*64})
  assert denied.status_code==409,(denied.status_code,denied.text)
  metadata={"reason":approval["reason_text"],"decision":"WEIGHT_TOLERANCE","expected_weight_policy_version":approval["expected_weight_policy_version"],
    "expected_content_version":approval["expected_content_version"],"expected_order_weight_signature":approval["expected_order_weight_signature"]}
  command={"contract_version":2,"operation_id":approval["operation_id"],"command_type":"CASE_SHORT_APPROVE","actor":"admin",
    "source":{"short_id":short_id},"lines":[],"units":[],"metadata":metadata}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  key="STOCK:"+sha256(approval["operation_id"].encode()).hexdigest().upper()
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select STATUS,WEIGHT_DECISION_OPERATION,INVENTORY_TASK_ID from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);assert q.fetchone()==("ACCEPTED",approval["operation_id"],None)
   q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:p_key",p_key=key);assert q.fetchone()==(1,)
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS,WEIGHT_DECISION_OPERATION from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);assert q.fetchone()==("PENDING_APPROVAL",None)
  q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:p_key",p_key=key);assert q.fetchone()==(0,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(20,10)
  def approve():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    r=client.post(base+f"/shorts/{short_id}/approve",json=approval);assert r.status_code==200,(r.status_code,r.text);return r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:decisions=list(pool.map(lambda _:approve(),range(2)))
  assert decisions[0]==decisions[1]and decisions[0]["inventory_task_id"]is None
  q.execute("select WEIGHT_POLICY_VERSION,WEIGHT_TOLERANCE_PCT,WEIGHT_ORDER_REQUESTED_KG,WEIGHT_ORDER_PICKED_KG,WEIGHT_DECISION_OPERATION from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id)
  policy_version,pct,original,actual,decision_op=q.fetchone();assert(policy_version,pct,original,actual,decision_op)==(1,15,10,9.6,approval["operation_id"])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(20,9.6)
  q.execute("select PICKED_QTY,STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()==(9.6,"SHORT_PICKED")
  try:q.execute("update RRL_CASE_PICK_SHORT set WEIGHT_TOLERANCE_PCT=100 where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);raise AssertionError("Original approval changed")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  print("PASS192 exact9.6/10 within15 explicit signed approval/no inventory discrepancy/P20H9.6/SHORT_PICKED/outer rollback outbox+decision+reserve/concurrent saved replay/stale409/immutable proof",approval["operation_id"],short_id,flush=True)
'''
t=t[:pos]+section+t[pos:]
print(json.dumps({"scripts/ni042_order_weight_decision_case.py":t},ensure_ascii=True))
