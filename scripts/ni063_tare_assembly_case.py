"""Own empty HU bookings, availability protection, and existing CASE snapshot."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088";p="/api/inventory/tare"
client=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select QUANTITY,BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3 and CONDITION_CODE='GOOD' and CUSTODIAN_KIND='WAREHOUSE'")
 quantity,version=q.fetchone();assert quantity==4
 booked=[];containers=[]
 for idx in range(5):
  identifier=f"TARE.HU:{tag}:{idx}";containers.append(identifier)
  call("/api/warehouse-hus/create",{"operation_id":f"TARE.HU.CREATE:{tag}:{idx}","identifier":identifier,"cell":"FG-A01-01","warehouse":9104,"container_type":"ROLL_CAGE","tare_weight_kg":"1","scan_container":identifier,"scan_cell":"FG-A01-01"})
  body={"operation_id":f"TARE.BOOK:{tag}:{idx}","place_kind":"HU","place_id":identifier,"pallet_type_id":3}
  if idx==4:
   error=call(p+"/book",body,409);assert "TARE_GOOD_WAREHOUSE_AVAILABILITY_REQUIRED" in error["detail"]["message"];break
  result=call(p+"/book",body);assert result["available_quantity"]==str(3-idx) and not result["physical_tare_changed"]
  assert call(p+"/book",body)==result;booked.append(body)
 rows=call(p+"/warehouses/9104/availability");own=next(r for r in rows if r["pallet_type_id"]==3)
 assert(own["physical_quantity"],own["assembly_quantity"],own["available_quantity"])==("4","4","0")
 error=call(p+"/count",{"operation_id":"TARE.COUNT.HELD:"+tag,"owner_ware_id":9104,"pallet_type_id":3,"condition":"GOOD","observed_quantity":"0","expected_version":own["balance_version"],"reason":"Cannot erase active assembly","decision_reference":"BLOCK:"+tag},409)
 assert "TARE_COUNT_BELOW_ASSEMBLY_HOLD" in error["detail"]["message"]
 error=call(p+"/damage",{"operation_id":"TARE.DAMAGE.HELD:"+tag,"owner_ware_id":9104,"pallet_type_id":3,"custodian_kind":"WAREHOUSE","custodian_id":"9104","quantity":"1","reason":"Booked asset cannot be spent","decision_reference":"BLOCK:"+tag},409)
 assert "TARE_SOURCE_HELD_FOR_ASSEMBLY" in error["detail"]["message"]
 for body in booked:
  cancel={"operation_id":body["operation_id"].replace("TARE.BOOK:","TARE.BOOK.CANCEL:"),"booking_operation_id":body["operation_id"]}
  result=call(p+"/book-cancel",cancel);assert result["status"]=="CANCELLED" and call(p+"/book-cancel",cancel)==result
 rows=call(p+"/warehouses/9104/availability");own=next(r for r in rows if r["pallet_type_id"]==3);assert own["available_quantity"]=="4"
 q.execute("select count(*) from RRL_REMAINS where UID_POLETA in(:a,:b,:d,:e,:f)",a=containers[0],b=containers[1],d=containers[2],e=containers[3],f=containers[4]);assert q.fetchone()==(0,)
 # Existing unused CASE from a prior own dev wave, no fabricated CASE/source engine.
 q.execute("select WARE_ID,PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1020 and STATUS='NEW' and STARTED_AT is null")
 case_ware,case_type=q.fetchone()
 rows=call(p+f"/warehouses/{case_ware}/availability");current=next(r for r in rows if r["pallet_type_id"]==case_type)
 assert current["count_state"]=="OBSERVATION_REQUIRED"
 call(p+"/count",{"operation_id":"TARE.CASE.COUNT:"+tag,"owner_ware_id":case_ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own software fixture opening count for existing CASE","decision_reference":"CASE1020:"+tag})
 case={"operation_id":"TARE.CASE.BOOK:"+tag,"place_kind":"CASE","place_id":"1020"}
 call(p+"/book",case)
 q.callproc("RRL_TARE_PLANNING.require_case",[1020,case_ware,case_type])
 snapshot=call("/api/case-pick/tasks/1020");assert snapshot["tare"]["booking_operation_id"]==case["operation_id"] and snapshot["tare"]["available_quantity"]=="0"
 call(p+"/book-cancel",{"operation_id":"TARE.CASE.CANCEL:"+tag,"booking_operation_id":case["operation_id"]})
 try:q.callproc("RRL_TARE_PLANNING.require_case",[1020,case_ware,case_type]);raise AssertionError("Unbooked CASE admitted")
 except oracledb.DatabaseError as exc:assert "CASE_ASSEMBLY_GOOD_TARE_BOOK_REQUIRED" in str(exc)
 print("PASS101 four existing HU bookings over warehouse4, fifth denied; active holds protected from count/damage, empty cancel/replay restores4, goods remains0; existing CASE1020 book/snapshot/start-rule/cancel")
