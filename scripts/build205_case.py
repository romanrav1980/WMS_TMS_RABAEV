from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-11_ni042_final_qc/004_qc.sql");s=p.read_text(encoding="utf-8").replace("raise_application_error(-20890,'QUALITY_SCANNED_COMPOSITION_CHANGED')","raise_application_error(-20873,'QUALITY_SCANNED_COMPOSITION_CHANGED')")
out[str(p)]=s
s=Path("scripts/ni042_final_scale_case.py").read_text(encoding="utf-8").replace("204","205")
s=s.replace("from datetime import", "from concurrent.futures import ThreadPoolExecutor\nfrom datetime import",1)
s=s.replace("case_types=set();sender=None","case_types=set();sender=None;controller=None")
needle='   tare_packet=final_packet'
pos=s.index(needle)
s=s[:pos]+"""   minimal=json.dumps({"metadata":{},"source":{"case_task_id":case}})
   try:q.callproc("RRL_CASE_SCALE_ADMISSION.assert_capture",[minimal,0]);raise AssertionError("First fill without actual empty tare admitted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20886
"""+s[pos:]
start=s.index('  check={"operation_id":"SMALL205.QC:"')
end=s.index('  after=quality.status(identifier)',start)
s=s[:start]+"""  controller="QC205"+tag;control_group=controller.upper();control_secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own final controller',:grp,:ware,0,0)",id=controller,secret=control_secret,grp=control_group,ware=ware);c.commit()
  call("POST","/api/admin/rights/groups",{"id":control_group,"name":"Own205 independent final controller"})
  call("POST",f"/api/admin/rights/groups/{control_group}/rights",{"right_name":"outgoing_pallet_check","description":"Own final controller"})
  qc_gateway=httpx.Client(auth=(controller,control_secret),timeout=35)
  final_path="/api/outgoing-quality/"+identifier+"/final-weight"
  check={"operation_id":"SMALL205.QC:"+tag,"capture_key":final_capture["capture_key"],"expected_composition_signature":before["composition_signature"]}
  raw={"operation_id":"SMALL205.MANUAL:"+tag,"quality_kind":"WEIGHT","gross_weight":"0.400","wood_weight":"0.100","expected_composition_signature":before["composition_signature"]}
  call("POST","/api/outgoing-quality/"+identifier+"/weight",raw,status=409)
  bad=qc_gateway.post(base+final_path,json={**check,"gross_weight":"0.400"});assert bad.status_code==422
  q.execute("select count(*)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=final_capture["capture_key"]);assert q.fetchone()[0]==0
  # Current native actor WARE is checked even for a saved APPLIED result.
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=controller);c.commit()
  refused=qc_gateway.post(base+final_path,json=check);assert refused.status_code==403
  q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=controller);c.commit()
  # One original native QC transaction: late rollback restores proof, approval, CASE and outbox.
  canonical=StockCommand(operation_id=check["operation_id"],command_type="OUTGOING_PALLET_CHECK",actor=controller,source={"pallet_identifier":identifier},lines=(),
      metadata={"quality_kind":"WEIGHT","gross_weight":final_capture["weight_kg"],"wood_weight":final_capture["tare_weight_kg"],"final_scale_capture":check["capture_key"],"expected_composition_signature":check["expected_composition_signature"]}).canonical_json()
  result=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,controller,result,None]);assert result.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
   assert read_oracle_json(result.getvalue())["ready"]
   q.execute("select count(*)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);assert q.fetchone()[0]==1
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=check["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select PROOVED,WEIGHT_QC_OPERATION_ID from RRL_SBORKA_PALLETS where ID=:p_id",p_id=sid);previous=q.fetchone();assert (previous[0]or 0)==0 and previous[1]is None
  q.execute("select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);assert q.fetchone()[0]=="WAIT_CONTROL"
  print("PASS205 late native QC rollback removes final-use/journal/approval and restores WAIT_CONTROL",flush=True)
  checks=[check,{**check,"operation_id":"SMALL205.QC.B:"+tag}]
  with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(lambda payload:qc_gateway.post(base+final_path,json=payload),checks))
  assert sorted(r.status_code for r in responses)==[200,409],[(r.status_code,r.text[:1800])for r in responses]
  index=next(i for i,r in enumerate(responses)if r.status_code==200);check=checks[index];verified=responses[index].json()
  assert verified["verified"]==1 and verified["ready"]
  replay=qc_gateway.post(base+final_path,json=check);assert replay.status_code==200 and replay.json()==verified
  q.execute("select count(*),max(STOCK_OPERATION_ID)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);assert q.fetchone()==(1,check["operation_id"])
  try:q.execute("delete from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);raise AssertionError("Scale use deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=controller);c.commit()
  refused=qc_gateway.post(base+final_path,json=check);assert refused.status_code==403
  try:q.callproc("RRL_STOCK_POSTING_API.prepare_command",[StockCommand(operation_id=check["operation_id"],command_type="OUTGOING_PALLET_CHECK",actor=controller,source={"pallet_identifier":identifier},lines=(),metadata={"quality_kind":"WEIGHT","gross_weight":final_capture["weight_kg"],"wood_weight":final_capture["tare_weight_kg"],"final_scale_capture":check["capture_key"],"expected_composition_signature":check["expected_composition_signature"]}).canonical_json(),controller,result,None]);raise AssertionError("Foreign native QC replay admitted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20882
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=controller);c.commit()
  used=call("GET",scale_base+f"/final-captures?task={case}");assert used["use_by_capture"][check["capture_key"]]["operation_id"]==check["operation_id"]
  print("PASS205 native once-only final GROSS/current source/tare exactly once/independent actor/concurrent distinctOP1winner/replay/manual bypass refused/current WARE before saved replay/immutable use",check["operation_id"],flush=True)
"""+s[end:]
needle='  if sender is not None:q.execute'
pos=s.index(needle);s=s[:pos]+"""  if controller is not None:q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor=controller);c.commit()
"""+s[pos:]
out["scripts/ni042_final_qc_case.py"]=s
out["db/migrations/2026-10-11_ni042_final_qc/010_client_stale.sql"]="@@004_qc.sql\n"
print(json.dumps(out,ensure_ascii=True))
