import sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
users=[("QCE"+tag,uuid4().hex),("QCS"+tag,uuid4().hex),("QCK"+tag,uuid4().hex)];case="STORE.WEIGHT:948fbd9a72:22c5dc5ec4"
def api(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();ware=2378876
 for actor,secret in users:
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own case closure role',:grp,:ware,0,0)",id=actor,secret=secret,grp=actor.upper(),ware=ware)
 c.commit()
 clients=[httpx.Client(auth=values,timeout=35)for values in users]
 try:
  for index,(actor,secret)in enumerate(users):
   api(admin,"POST","/api/admin/rights/groups",{"id":actor.upper(),"name":"Own case closure"})
   rights=["store_case_investigate","store_loss_confirm"]if index<2 else ["store_case_manage","store_loss_confirm"]
   for right in rights:api(admin,"POST",f"/api/admin/rights/groups/{actor.upper()}/rights",{"right_name":right,"description":"Own case closure"})
  exp,sec,kro=clients;prefix="/api/delivery/case-work/"+case
  closure={"operation_id":"CASE.CLOSE:"+tag,"expected_version":1,"reason":"Own full quantity investigation: original mass exception reviewed, no new warehouse quantity effect","decision_reference":"KRO:"+tag}
  api(kro,"POST",prefix+"/close",closure,409)
  assignment={"operation_id":"CASE.CLOSE.ASSIGN:"+tag,"expected_version":1,"expedition_user":users[0][0],"security_user":users[1][0],"search_deadline":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(timespec="microseconds")}
  api(kro,"POST",prefix+"/assign",assignment)
  api(kro,"POST",prefix+"/close",{**closure,"operation_id":"CASE.BAD.FINDINGS:"+tag,"expected_version":2},409)
  first={"operation_id":"CASE.CLOSE.EXP:"+tag,"expected_version":2,"role":"EXPEDITION","report":"Own original quantity and physical weight evidence reviewed"}
  api(exp,"POST",prefix+"/finding",first)
  api(sec,"POST",prefix+"/finding",{**first,"operation_id":"CASE.CLOSE.SEC:"+tag,"expected_version":3,"role":"SECURITY","report":"Own independent source and mass-exception conclusion"})
  closure["expected_version"]=4
  denied=api(exp,"POST",prefix+"/close",{**closure,"operation_id":"CASE.BAD.SELF.CLOSE:"+tag},403);assert "CASE_CLOSE_INDEPENDENT_KRO_REQUIRED"in denied["detail"]["message"]
  api(kro,"GET","/api/delivery/case-work/STORE.RECEIPT:bea258a7dd/management",status=403)
  source=api(admin,"GET","/api/delivery/case-work/STORE.RECEIPT:bea258a7dd/loss-review")
  denied=api(admin,"POST","/api/delivery/case-work/STORE.RECEIPT:bea258a7dd/close",{**closure,"operation_id":"CASE.BAD.OPEN.OBL:"+tag,"expected_version":source["case_version"]},409);assert "CASE_CLOSE_UNRESOLVED_QUANTITY_OBLIGATIONS"in denied["detail"]["message"]
  result=api(kro,"POST",prefix+"/close",closure);assert result["status"]=="CLOSED"and not result["warehouse_stock_changed"]and result["case_version"]==5
  assert api(kro,"POST",prefix+"/close",closure)==result
  dossier=api(kro,"GET",prefix+"/loss-review");assert dossier["status"]=="CLOSED"
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=closure["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_STORE_CASE_CLOSURE where OPERATION_ID=:op",op=closure["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='STORE_DISCREPANCY_CLOSED'and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=closure["operation_id"]);assert q.fetchone()[0]==1
  print("PASS117 existing ordinary full-quantity mass case/original two findings/independent warehouse-bound KRO/CLOSEDv5/immutable closure/SAP pending1/replay/no goods; unresolved original excess and foreign case denied; tag="+tag,flush=True)
 finally:
  for actor,secret in users:q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor)
  c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_STORE_CASE_CLOSURE%'and upper(SQL_TEXT)not like '%V$SQL%'and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
