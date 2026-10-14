"""Own approved source/SAP binding on existing real departed author trip."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
client=httpx.Client(auth=("admin","admin123"),timeout=30)
def call(method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor();q.execute("""
 select a.OPERATION_ID,f.TT_ID,f.VEHICLE_ID from RRL_STORE_RETURN_APPROVAL a
 join RRL_STORE_RETURN_SAP s on s.APPROVAL_OPERATION_ID=a.OPERATION_ID
 join RRL_STORE_RECEIPT_FACT r on r.OPERATION_ID=a.RECEIPT_OPERATION_ID
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd' and a.DISPOSITION='SUPPLIER'
 """);approval,trip,vehicle=q.fetchone()
 path="/api/delivery/store-return-transport"
 rows=call("GET",path+"/eligible");assert any(x["approval_id"]==approval for x in rows)
 body={"operation_id":"RETURN.TRANSPORT:"+tag,"approval_operation_id":approval,"task_id":int(trip),"gross_weight_kg":"2","physical_places":1}
 bad=call("POST",path+"/plan",{**body,"operation_id":"RETURN.TR.BAD.CAP:"+tag,"gross_weight_kg":"999999999"},409);assert "STORE_RETURN_CONSERVATIVE_CAPACITY_EXCEEDED" in bad["detail"]["message"],bad
 bad=call("POST",path+"/plan",{**body,"operation_id":"RETURN.TR.BAD.SAP:"+tag,"approval_operation_id":"ABSENT"},409);assert "STORE_RETURN_APPROVAL_SAP_TRIP_CONFIGURATION_REQUIRED" in bad["detail"]["message"],bad
 q.execute("select nvl(sum(GROSS_WEIGHT_KG),0),count(*) from RRL_TT_HU_LOAD_FACT where TT_ID=:tt and STATUS in('LOADED','DEPARTED')",tt=trip);loaded,loaded_places=q.fetchone()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=:cap,PALLETS=:places where ID=:id",cap=loaded+2,places=loaded_places+1,id=vehicle);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 result=call("POST",path+"/plan",body);assert result["task_id"]==trip and result["status"]=="PLANNED_PICKUP" and not result["physical_pickup_confirmed"] and not result["warehouse_stock_changed"],result
 assert call("POST",path+"/plan",body)==result
 bad=call("POST",path+"/plan",{**body,"operation_id":"RETURN.TR.DUP:"+tag},409);assert "STORE_RETURN_ALREADY_PLANNED" in bad["detail"]["message"],bad
 manifest=call("GET",path+"/trips/"+str(trip));assert any(x["operation_id"]==body["operation_id"] and x["gross_weight_kg"]=="2" and x["physical_places"]==1 for x in manifest)
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(0,)
 q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
 try:q.execute("delete from RRL_STORE_RETURN_TRANSPORT where OPERATION_ID=:op",op=body["operation_id"]);c.commit();raise AssertionError("Plan deleted")
 except oracledb.DatabaseError as exc:c.rollback();assert "STORE_RETURN_TRANSPORT_HISTORY_IMMUTABLE" in str(exc)
print("PASS094 actual existing trip/SAP warehouse/capacity2kg1place/source/oversize/retry/duplicate/immutable/outbox1/events0; pickup remains explicit",flush=True)
