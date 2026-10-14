import sys
from pathlib import Path
from uuid import uuid4
from hashlib import sha256
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QSH"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();dispatch="SUP.LOAD:f877bb1524"
 q.execute("select r.WARE_ID from RRL_STORE_RETURN_SUP_DISPATCH d join RRL_STORE_RETURN_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID where d.OPERATION_ID=:op",op=dispatch);ware=q.fetchone()[0]
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own supplier document observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own supplier handover"})
 for right in ["warehouse_return_dispatch","store_return_approve"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own supplier documentary handover"})
 try:
  p="/api/inventory/supplier-handover"
  report={"operation_id":"SUP.DOC:"+tag,"dispatch_operation_id":dispatch,"document_reference":"DEV.DOCUMENT:"+tag,"document_sha256":sha256(("Own software fixture only "+tag).encode()).hexdigest(),"receiver_name":"Own simulated supplier receiver"}
  fact=api(user,p+"/record",report);assert api(user,p+"/record",report)==fact and not fact["stock_changed"]
  api(user,p+"/record",{**report,"receiver_name":"Changed"},409)
  decision={"operation_id":"SUP.CONFIRM:"+tag,"handover_operation_id":report["operation_id"],"document_reference":"SC:"+tag,"reason":"Own independent documentary fixture decision"}
  api(user,p+"/confirm",decision,403)
  result=api(admin,p+"/confirm",decision);assert result["status"]=="HANDOVER_CONFIRMED" and api(admin,p+"/confirm",decision)==result
  api(admin,p+"/confirm",{**decision,"operation_id":"SUP.SECOND:"+tag},409)
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='SUPPLIER_RETURN_HANDED_OVER' and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=decision["operation_id"]);assert q.fetchone()==(1,)
  for op in [report["operation_id"],decision["operation_id"]]:
   q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='INTERNAL.RETURN:6b388966d1' and CELL='QRPSdab5c00141'");assert q.fetchone()==(0,0)
  queue=api(admin,p+f"/warehouses/{ware}");assert any(x["confirmation_operation_id"]==decision["operation_id"] for x in queue)
  print("PASS109 documentary handover on original actually departed108, non-admin bound reporter/replay/payload conflict, same actor403/independent SC/replay/second409/SAP pending1, P0H0/no goods event; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_SUP_RETURN_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
