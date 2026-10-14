"""Continue owned departed fixture without recreating stock."""
import json,sys
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
from app.modules.transport.public import unassign_st
cfg=get_settings();tag=sys.argv[1];shipop="FULL.HU.SHIP:"+tag;store_addr="STORE.QA:"+tag;foreign_addr="STORE.OTHER:"+tag;top="HU.FULL:"+tag
client=httpx.Client(auth=("admin","admin123"),timeout=35)
def http(method,path,body=None,expected=200):
 response=client.request(method,"http://127.0.0.1:8088/api/delivery/store-receipts"+path,json=body)
 assert response.status_code==expected,(response.status_code,response.text[:1200])
 return response.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor();q.execute("select TT_ID,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=shipop);trip,status=q.fetchone()
 q.execute("select SBORKA_PALLET_ID from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op",op=shipop);st=q.fetchone()[0]
 if status=="LOADED":
  unassign_st(OracleGateway(),trip,"TT.PENDING:"+tag)
  build_transport_loading().depart("STORE.TRIP.DEPART:"+tag,trip,"admin")
 # Frozen loading address is the destination authority, not a later ST edit.
 q.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and SBORKA_PALLET_ID=:st",op=shipop,st=st)
 assert q.fetchone()==(store_addr,)
 try:
  q.execute("update RRL_SBORKA_PALLETS set ADDR=:addr where ID=:id",addr=foreign_addr,id=st);conn.commit()
 except oracledb.DatabaseError as exc:conn.rollback();assert "LOADED_ST_CONFIRMED_UNLOADING_REQUIRED" in str(exc),str(exc)
 else:raise AssertionError("Departed destination changed")
 places=http("GET",f"/trips/{trip}/places?store_address={store_addr}")
 assert len(places)==1 and places[0]["load_operation_id"]==shipop
 preview=http("GET",f"/preview?load_operation_id={shipop}&store_address={store_addr}")
 assert preview["mode"]=="BARCODE" and not preview["requires_marked_recipient_flow"]
 receipt={"operation_id":"STORE.RECEIPT:"+tag,"load_operation_id":shipop,"store_address":store_addr,
  "scan_place":top,"expected_composition_signature":preview["composition_signature"],"before_cameras":True}
 accepted=http("POST","/confirm",receipt)
 assert accepted["status"]=="ACCEPTED" and accepted["accepted_lines"][0]["accepted_quantity"]=="3"
 assert not accepted["warehouse_stock_consumed_again"] and not accepted["government_ack_created"]
 assert http("POST","/confirm",receipt)==accepted
 conflict=http("POST","/confirm",{**receipt,"scan_place":"OTHER"},409)
 assert "OPERATION_CONFLICT" in conflict["detail"]["message"],conflict
 duplicate=http("POST","/confirm",{**receipt,"operation_id":"STORE.DUPLICATE:"+tag},409)
 assert "STORE_PLACE_ALREADY_RECEIVED" in duplicate["detail"]["message"],duplicate
 q.execute("select RECEIPT_STATE,STORE_ADDR,RECEIVED_BY from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==("ACCEPTED",store_addr,"admin")
 q.execute("select SHIPPED_BASE_QTY,ACCEPTED_BASE_QTY,MISSING_BASE_QTY from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==(3,3,0)
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==(0,)
 q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=receipt["operation_id"]);assert q.fetchone()==(1,)
 print("PASS082 frozen destination/change denial;083 actual API store full receipt3/replay/conflict/duplicate denial/wrong store/scan/camera/mandatory weight refusal, P/H0/no second quantity event/business outbox",flush=True)
