import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QIF"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();load="INTERWARE.NEXT.LOAD:f755e2320c";lot="FULL.QA:9b15cf997d";address="Own full-pallet ST";order=1902
 before=api(admin,"GET",f"/api/customer-orders/{order}/delivery");assert before["delivery_status"]=="WAITING_FOR_RECEIPT" and before["quantities"][0]["shipped"]=="3" and before["quantities"][0]["unreceived"]=="3",before
 q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()==(0,),"Continue already committed final store receipt"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own final store receiver',:grp,9104,0,0)",id=actor,secret=secret,grp=group);c.commit()
 api(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own final store receiver"})
 api(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"store_receipt_confirm","description":"Own final store receiver"})
 q.execute("select count(*)from RRL_ADDR where ADDR=:addr",addr=address)
 if q.fetchone()[0]==0:
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute("insert into RRL_ADDR(ADDR)values(:addr)",addr=address);c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select POLICY_VERSION from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:addr",addr=address);old=q.fetchone()
 p="/api/delivery/store-receipts"
 if not old:api(admin,"PUT",p+"/policy",{"store_address":address,"mode":"BARCODE","expected_version":0})
 api(admin,"POST",p+"/receivers",{"store_address":address,"username":actor})
 try:
  preview=api(user,"GET",p+f"/preview?load_operation_id={load}&store_address={address}")
  body={"operation_id":"INTERWARE.FINAL.RECEIPT:"+tag,"load_operation_id":load,"store_address":address,"scan_place":lot,"expected_composition_signature":preview["composition_signature"],"before_cameras":True}
  api(user,"POST",p+"/confirm",{**body,"operation_id":"INTERWARE.FINAL.BADSCAN:"+tag,"scan_place":"FOREIGN"},409)
  accepted=api(user,"POST",p+"/confirm",body);assert accepted["status"]=="ACCEPTED" and accepted["accepted_lines"][0]["accepted_quantity"]=="3" and not accepted["warehouse_stock_consumed_again"]
  assert api(user,"POST",p+"/confirm",body)==accepted
  api(user,"POST",p+"/confirm",{**body,"operation_id":"INTERWARE.FINAL.SECOND:"+tag},409)
  after=api(admin,"GET",f"/api/customer-orders/{order}/delivery")
  assert after["delivery_status"]=="RECEIVED_SHIPPED_VOLUME" and after["quantities"][0]["shipped"]=="3" and after["quantities"][0]["accepted"]=="3" and after["quantities"][0]["unreceived"]=="0",after
  assert after["receipt_lineage"][0]["original_load_operation_id"]=="SINGLE.FULL.LOAD:9b15cf997d" and after["receipt_lineage"][0]["actual_final_load_operation_id"]==load
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=lot);assert q.fetchone()==(0,0)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(0,)
  q.execute("select STATUS,FACT_QTY,FACT_UOM,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=64");assert q.fetchone()==("SHIPPED",3,"EA","SINGLE.FULL.LOAD:9b15cf997d")
  print("PASS123 original1902 unreceived3 until actual final store/current bound receiver/wrongscan/second denied/replay/final accepted3 only/original-to-onward receipt lineage/no duplicate shipped count/P0H0/no goods/customer64 unchanged; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_ONWARD_DISPATCH%'and upper(SQL_TEXT) not like '%V$SQL%'and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
