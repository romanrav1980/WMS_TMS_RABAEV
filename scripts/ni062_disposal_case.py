import sys
from pathlib import Path
from uuid import uuid4
from hashlib import sha256
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QDC"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();receipt="DISPOSAL.RECEIVE:b10092cbf0"
 q.execute("select r.WARE_ID,r.UID_PALLET,x.CELL,x.STOCK_VERSION from RRL_STORE_RETURN_RECEIPT r join RRL_REMAINS x on x.UID_POLETA=r.UID_PALLET and x.REMAIN>0 where r.OPERATION_ID=:op",op=receipt);ware,lot,cell,version=q.fetchone()
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own destruction observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own destruction observer"})
 for right in ["warehouse_return_dispatch","store_return_approve"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own independent destruction scenario"})
 try:
  p="/api/inventory/return-disposal"
  report={"operation_id":"DISPOSAL.DOC:"+tag,"receipt_operation_id":receipt,"document_reference":"DEV.DESTRUCTION:"+tag,"document_sha256":sha256(("Own software fixture only "+tag).encode()).hexdigest(),"reason":"Own simulated destruction document"}
  fact=api(user,p+"/report",report);assert api(user,p+"/report",report)==fact and not fact["stock_changed"]
  body={"operation_id":"DISPOSAL.POST:"+tag,"request_operation_id":report["operation_id"],"expected_stock_version":version,"scan_pallet":lot,"scan_cell":cell,"decision_reference":"SC:"+tag}
  api(user,p+"/dispose",body,403)
  api(admin,p+"/dispose",{**body,"operation_id":"DISPOSAL.BAD.VERSION:"+tag,"expected_stock_version":version+1},409)
  api(admin,p+"/dispose",{**body,"operation_id":"DISPOSAL.BAD.CELL:"+tag,"scan_cell":"FOREIGN.CELL"},409)
  result=api(admin,p+"/dispose",body);assert result["status"]=="DISPOSED" and result["loss_store_addr"]=="STORE.QA:04633c677f"
  assert api(admin,p+"/dispose",body)==result
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=lot,cell=cell);assert q.fetchone()==(0,0)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  q.execute("select count(*)from RRL_RETURN_DISPOSAL_FACT where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='STORE_RETURN_DISPOSED' and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  api(admin,p+"/dispose",{**body,"operation_id":"DISPOSAL.SECOND:"+tag},409)
  print("PASS110 actual disposal1 blocked source/current scans/version, non-admin report/replay/same actor403/stale and foreign denied/independent root/P0H0/event1/fact1/SAP pending1/loss original store/replay/second denied; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_RETURN_DISPOSAL%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
