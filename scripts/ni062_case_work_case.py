"""Own ordinary shortage: dispatcher, two real investigators and independent KRO."""
import sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];case="STORE.RECEIPT:bea258a7dd";base="http://127.0.0.1:8088"
admin=httpx.Client(auth=("admin","admin123"),timeout=30)
users=[("QEX"+tag,"QE"+tag.upper(),uuid4().hex),("QSE"+tag,"QZ"+tag.upper(),uuid4().hex)]
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1400]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor()
 for username,group,password in users:
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own case investigator',:grp,0,0)",id=username,secret=password,grp=group)
 conn.commit()
 try:
  for username,group,password in users:
   call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own case investigation"})
   call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"store_case_investigate","description":"Own investigation role"})
  exp=httpx.Client(auth=(users[0][0],users[0][2]),timeout=30);sec=httpx.Client(auth=(users[1][0],users[1][2]),timeout=30)
  source=call(admin,"GET","/api/delivery/store-receipts/cases/"+case);version=source["case_version"];assert version==1,source
  prefix="/api/delivery/case-work/"+case
  assignment={"operation_id":"CASE.ASSIGN:"+tag,"expected_version":version,"expedition_user":users[0][0],"security_user":users[1][0],"search_deadline":(datetime.now(timezone.utc)+timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")}
  refused=call(admin,"POST",prefix+"/assign",{**assignment,"operation_id":"CASE.BAD.SAME:"+tag,"security_user":users[0][0]},status=409);assert "CASE_SEPARATE_INVESTIGATORS_REQUIRED" in refused["detail"]["message"]
  result=call(admin,"POST",prefix+"/assign",assignment);assert result["case_version"]==2 and not result["warehouse_stock_changed"],result
  assert call(admin,"POST",prefix+"/assign",assignment)==result
  queue=call(exp,"GET","/api/delivery/case-work/mine");assert any(row["case_id"]==case for row in queue)
  view=call(sec,"GET",prefix+"/investigation");assert view["expedition_user"]==users[0][0] and view["security_user"]==users[1][0]
  report={"operation_id":"CASE.EXP:"+tag,"expected_version":2,"role":"EXPEDITION","report":"Own expedition search: original missing unit not found; excess kept separate"}
  refused=call(sec,"POST",prefix+"/finding",report,status=403);assert "CASE_ASSIGNED_INVESTIGATOR_ONLY" in refused["detail"]["message"]
  findings=call(exp,"POST",prefix+"/finding",report);assert findings["case_version"]==3
  assert call(exp,"POST",prefix+"/finding",report)==findings
  loss={"operation_id":"CASE.LOSS:"+tag,"expected_version":3,"line_no":1,"reason":"Own KRO decision based on both search reports"}
  refused=call(admin,"POST",prefix+"/loss",loss,status=409);assert "CASE_BOTH_INVESTIGATOR_FINDINGS_REQUIRED" in refused["detail"]["message"]
  sec_report={"operation_id":"CASE.SEC:"+tag,"expected_version":2,"role":"SECURITY","report":"Own security review: original source and search checked"}
  stale=call(sec,"POST",prefix+"/finding",sec_report,status=409);assert "CASE_VERSION_CONFLICT" in stale["detail"]["message"]
  sec_report["expected_version"]=3
  done=call(sec,"POST",prefix+"/finding",sec_report);assert done["case_version"]==4
  loss["expected_version"]=4
  call(exp,"POST",prefix+"/loss",loss,status=403)
  call(admin,"POST",f"/api/admin/rights/groups/{users[0][1]}/rights",{"right_name":"store_loss_confirm","description":"Own segregation refusal test"})
  refused=call(exp,"POST",prefix+"/loss",{**loss,"operation_id":"CASE.BAD.SELFLOSS:"+tag},status=403)
  assert "CASE_LOSS_INDEPENDENT_KRO_REQUIRED" in refused["detail"]["message"],refused
  recognized=call(admin,"POST",prefix+"/loss",loss);assert recognized["loss_quantity"]=="1" and recognized["base_uom"]=="EA" and recognized["case_version"]==5
  assert not recognized["warehouse_stock_changed"] and not recognized["government_ack_created"]
  assert call(admin,"POST",prefix+"/loss",loss)==recognized
  duplicate=call(admin,"POST",prefix+"/loss",{**loss,"operation_id":"CASE.LOSS.DUP:"+tag,"expected_version":5},status=409)
  assert "CASE_MISSING_OBLIGATION_ALREADY_DECIDED" in duplicate["detail"]["message"]
  dossier=call(admin,"GET",prefix+"/loss-review")
  assert dossier["case_version"]==5 and len(dossier["findings"])==2 and dossier["losses"][0]["base_qty"]=="1"
  assert next(row for row in dossier["obligations"] if row["kind"]=="MISSING_INVESTIGATION")["status"]=="LOSS_CONFIRMED"
  assert next(row for row in dossier["obligations"] if row["kind"]=="EXCESS_REVIEW")["status"]=="OPEN"
  for operation in (assignment["operation_id"],report["operation_id"],sec_report["operation_id"],loss["operation_id"]):
   q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=operation);assert q.fetchone()==(0,)
   q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=operation);assert q.fetchone()==(1,)
  q.execute("select count(*) from RRL_REMAINS where UID_POLETA='FULL.QA:bea258a7dd' and (REMAIN!=0 or HARD_RESERVED_BASE!=0)");assert q.fetchone()==(0,)
  try:q.execute("update RRL_STORE_DISCREPANCY_CASE set CASE_VERSION=99 where CASE_ID=:id",id=case);conn.commit();raise AssertionError("Case changed directly")
  except oracledb.DatabaseError as exc:conn.rollback();assert "STORE_CASE_ROOT_REQUIRED" in str(exc)
  print("PASS091 actual dispatcher/deadline/separate real investigators/findings/stale version/role/independent KRO loss1/replay/duplicate denial; source stock0/outbox1 per step/quantity events0; excess separate",flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)",a=users[0][0],b=users[1][0]);conn.commit()
