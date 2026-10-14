import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];p="/api/inventory/tare";base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def api(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
def call(client,path,body=None,status=200):return api(client,"POST" if body else "GET",path,body,status)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("""select d.CLAIM_KEY,d.STORE_ADDR,d.ACCEPT_OPERATION_ID,d.POLICY_VERSION,to_char(d.EFFECTIVE_DUE_AT,'YYYY-MM-DD HH24:MI:SS TZH:TZM'),a.ACCEPTED_BY,u.PASS,u.USER_GROUP
 from RRL_TARE_STORE_DEBT d join RRL_TARE_ACCEPT a on a.OPERATION_ID=d.ACCEPT_OPERATION_ID join RUSERS u on u.ID=a.ACCEPTED_BY
 where d.OWNER_WARE_ID=9104 and d.PALLET_TYPE_ID=3 and d.CONDITION_CODE='DAMAGED' and d.OUTSTANDING_QTY=1 and a.ACCEPTED_BY like 'QTS%'""")
 claim,store,delivery,policy,due,observer,secret,group=q.fetchone()
 q.execute("update RUSERS set DELETED=0 where ID=:id",id=observer);c.commit()
 try:
  call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":"tare_loss_report","description":"Own current store loss observation"})
  shop=httpx.Client(auth=(observer,secret),timeout=35)
  row=next(x for x in call(shop,p+"/warehouses/9104/balances") if x["custodian_kind"]=="STORE" and x["custodian_id"]==store and x["pallet_type_id"]==3 and x["condition_code"]=="DAMAGED")
  report={"operation_id":"LOSS.STORE.REPORT:"+tag,"owner_ware_id":9104,"pallet_type_id":3,"condition":"DAMAGED","custodian_kind":"STORE","custodian_id":store,"source_claim_id":claim,"quantity":"1","expected_version":row["balance_version"],"reason":"Own damaged asset missing at store","decision_reference":"OBS:"+tag}
  result=call(shop,p+"/loss-report",report);assert call(shop,p+"/loss-report",report)==result and not result["goods_stock_changed"]
  call(admin,p+"/writeoff",{"operation_id":"LOSS.BAD.DAMAGE.WRITE:"+tag,"damage_operation_id":claim,"quantity":"1","reason":"Cannot double consume pending claim","decision_reference":"BAD:"+tag},409)
  decision={"operation_id":"LOSS.STORE.WRITE:"+tag,"claim_operation_id":report["operation_id"],"outcome":"WRITE_OFF","reason":"Independent store loss decision","decision_reference":"LOSS:"+tag}
  call(shop,p+"/loss-decide",decision,403)
  result=call(admin,p+"/loss-decide",decision);assert call(admin,p+"/loss-decide",decision)==result
  q.execute("select OUTSTANDING_QTY,POLICY_VERSION,to_char(EFFECTIVE_DUE_AT,'YYYY-MM-DD HH24:MI:SS TZH:TZM') from RRL_TARE_STORE_DEBT where CLAIM_KEY=:claim",claim=claim);assert q.fetchone()==(0,policy,due)
  q.execute("select QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3 and CONDITION_CODE='DAMAGED' and CUSTODIAN_KIND='STORE' and CUSTODIAN_ID=:store",store=store);assert q.fetchone()==(0,)
  print("PASS106 bound store DAMAGED1 reported/blocked double writeoff/independent loss0/debt0 original deadline, replay/no goods",flush=True)
 finally:q.execute("update RUSERS set DELETED=1 where ID=:id",id=observer);c.commit()
 q.execute("""select b.OWNER_WARE_ID,l.TT_ID,l.VEHICLE_ID,l.VEHICLE_NUMBER,tt.VODITEL_ID,bind.USER_ID,u.PASS,u.USER_GROUP,bal.BALANCE_VERSION
 from RRL_TARE_BOOK b join RRL_TARE_OFFER_BOOK x on x.BOOK_OPERATION_ID=b.OPERATION_ID join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=x.LOAD_OPERATION_ID
 join RRL_TRANSPORT_TASK tt on tt.ID=l.TT_ID join RRL_TRANSPORT_DRIVER_USER bind on bind.DRIVER_ID=tt.VODITEL_ID join RUSERS u on u.ID=bind.USER_ID
 join RRL_TARE_BALANCE bal on bal.OWNER_WARE_ID=b.OWNER_WARE_ID and bal.CUSTODIAN_KIND='VEHICLE' and bal.CUSTODIAN_ID=to_char(l.VEHICLE_ID,'TM9') and bal.PALLET_TYPE_ID=1 and bal.CONDITION_CODE='GOOD'
 where b.OPERATION_ID like 'TARE.FULL.BOOK:%' and b.STATUS='TRANSFERRED' and bal.QUANTITY=1 order by b.CLOSED_AT desc fetch first 1 row only""")
 ware,trip,vehicle,plate,driver,observer,secret,group,version=q.fetchone()
 binding=api(admin,"GET",f"/api/transport/driver-bindings/{driver}");assert not binding["active"]
 q.execute("update RUSERS set DELETED=0 where ID=:id",id=observer);c.commit()
 for right in ["tare_loss_report","tare_offer"]:
  call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own vehicle loss observer"})
 enabled=api(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":observer,"active":True,"expected_version":binding["binding_version"]})
 try:
  driver_client=httpx.Client(auth=(observer,secret),timeout=35)
  report={"operation_id":"LOSS.VEH.REPORT:"+tag,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","custodian_kind":"VEHICLE","custodian_id":str(vehicle),"task_id":trip,"scan_vehicle":plate,"quantity":"1","expected_version":version,"reason":"Own vehicle inspection suspicion","decision_reference":"OBS:"+tag}
  call(driver_client,p+"/loss-report",{**report,"operation_id":"LOSS.VEH.BAD:"+tag,"scan_vehicle":"OTHER"},409)
  call(driver_client,p+"/loss-report",report)
  call(driver_client,p+"/offer",{"operation_id":"LOSS.VEH.BAD.OFFER:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"VEHICLE","from_id":str(vehicle),"to_kind":"WAREHOUSE","to_id":str(ware),"quantity":"1","scan_vehicle":plate},409)
  decision={"operation_id":"LOSS.VEH.REJECT:"+tag,"claim_operation_id":report["operation_id"],"outcome":"REJECT","reason":"Asset located, original custody unchanged","decision_reference":"FOUND:"+tag}
  call(admin,p+"/loss-decide",decision)
  q.execute("select QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=1 and CUSTODIAN_KIND='VEHICLE'",ware=ware);assert q.fetchone()==(1,)
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID in(:a,:b)",a=report["operation_id"],b=decision["operation_id"]);assert q.fetchone()==(0,)
  print("PASS106 current bound driver exact vehicle/scan, pending loss blocks vehicle offer, independent reject retains vehicle1/no goods",flush=True)
 finally:
  api(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":observer,"active":False,"expected_version":enabled["binding_version"]})
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=observer);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%SOURCE_CLAIM_ID%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
