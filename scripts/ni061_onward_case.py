import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts
from app.transport_composition import build_transport_loading
from app.modules.inventory.public import StockCommand,StockPostingError,build_stock_posting_service
s=get_settings();tag=uuid4().hex[:10];actor="QIN"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();receipt="INTERWARE.RECEIVE:349bc1ff57"
 q.execute("select count(*)from RRL_INTERWARE_ONWARD_BIND where RECEIPT_OPERATION_ID=:op",op=receipt);assert q.fetchone()==(0,),"Continue original prepared ST"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own onward dispatcher',:grp,9104,0,0)",id=actor,secret=secret,grp=group);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own onward dispatcher"})
 for right in ["outgoing_pallet_edit","transport_dispatch_edit","transport_dispatch_view"]:api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own onward dispatcher"})
 try:
  p="/api/inventory/interwarehouse/prepare-onward";body={"operation_id":"INTERWARE.NEXT.PREPARE:"+tag,"receipt_operation_id":receipt,"reason":"Own ordinary two-leg cargo continuation","decision_reference":"NEXT:"+tag,"accept_legacy_address":True}
  prepared=api(user,p,body);assert prepared["quantity"]=="3" and not prepared["stock_changed"] and not prepared["customer_fulfillment_repeated"]
  print("Prepared existing onwardST "+str(prepared["st_id"])+" tag="+tag,flush=True)
  assert api(user,p,body)==prepared
  api(user,p,{**body,"reason":"Changed"},409)
  api(user,p,{**body,"operation_id":"INTERWARE.NEXT.SECOND:"+tag},409)
  identifier=prepared["shipment_identifier"];trip=prepared["target_trip_id"]
  q.execute("select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st",st=prepared["st_id"]);assert q.fetchone()==(0,)
  q.execute("select STATUS,FACT_QTY,FACT_UOM,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=64");assert q.fetchone()==("SHIPPED",3,"EA","SINGLE.FULL.LOAD:9b15cf997d")
  assign_sts(OracleGateway(),trip,[prepared["st_number"]])
  loading=build_transport_loading();preview=loading.preview_single(identifier);assert preview["root"]=="FULL.QA:9b15cf997d"
  posting=build_stock_posting_service()
  try:posting.post(StockCommand(operation_id="INTERWARE.BAD.LOGICAL:"+tag,command_type="SHIP_PALLET",actor="admin",source={"pallet_identifier":identifier},lines=(),metadata={}))
  except StockPostingError as exc:assert "INTERWARE_ONWARD_ACTUAL_LOADING_REQUIRED" in str(exc.rule_reason or exc),str(exc)
  else:raise AssertionError("Logical shipping impersonated actual onward loading")
  load_body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":preview["root"],"scan_cell":"QIOec6052b26e","loading_context":{"transport_task_id":trip,"scan_vehicle":"QIec6052b26e","scan_dock":"QIOec6052b26e","measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"2","width_m":"1","depth_m":"1","height_m":"1"}}}
  loaded=loading.load_single("INTERWARE.NEXT.LOAD:"+tag,identifier,load_body,"admin");assert loading.load_single("INTERWARE.NEXT.LOAD:"+tag,identifier,load_body,"admin")==loaded
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA='FULL.QA:9b15cf997d'");assert q.fetchone()==(0,0)
  q.execute("select count(*)from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:op",op="INTERWARE.NEXT.LOAD:"+tag);assert q.fetchone()==(1,)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op="INTERWARE.NEXT.LOAD:"+tag);assert q.fetchone()==(1,)
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='INTERWARE_ONWARD_DISPATCHED' and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op="INTERWARE.NEXT.LOAD:"+tag);assert q.fetchone()==(1,)
  departed=loading.depart("INTERWARE.NEXT.DEPART:"+tag,trip,"admin");assert not departed["stock_consumed_again"]
  q.execute("select STATUS,FACT_QTY,FACT_UOM,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=64");assert q.fetchone()==("SHIPPED",3,"EA","SINGLE.FULL.LOAD:9b15cf997d")
  print("PASS122 ordinary native constructor/rows/existing assignment/source-pinned whole3/original ownership64 unchanged/new fulfillment0/replay/second/conflict/logical deny/actual second load3P0H0/event1/outbox1/native departure0; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_ONWARD%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
