import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.transport_composition import build_transport_loading
s=get_settings();tag="f755e2320c"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("select b.ST_IDENTIFIER,b.TARGET_TT_ID,r.ROOT_UID,b.SOURCE_CELL,t.TRANSPORT,b.ORIGINAL_FULFILLMENT_JSON from RRL_INTERWARE_ONWARD_BIND b join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=b.RECEIPT_OPERATION_ID join RRL_TRANSPORT_TASK t on t.ID=b.TARGET_TT_ID where b.OPERATION_ID=:op",op="INTERWARE.NEXT.PREPARE:"+tag)
 identifier,trip,lot,cell,vehicle,ownership=q.fetchone()
 loading=build_transport_loading();preview=loading.preview_single(identifier)
 body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":cell,"loading_context":{"transport_task_id":trip,"scan_vehicle":vehicle,"scan_dock":cell,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"2","width_m":"1","depth_m":"1","height_m":"1"}}}
 op="INTERWARE.NEXT.LOAD:"+tag
 loaded=loading.load_single(op,identifier,body,"admin");assert loading.load_single(op,identifier,body,"admin")==loaded
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=lot);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,)
 q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='INTERWARE_ONWARD_DISPATCHED'and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=op);assert q.fetchone()==(1,)
 departed=loading.depart("INTERWARE.NEXT.DEPART:"+tag,int(trip),"admin");assert not departed["stock_consumed_again"]
 q.execute("select STATUS,FACT_QTY,FACT_UOM,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=64");assert q.fetchone()==("SHIPPED",3,"EA","SINGLE.FULL.LOAD:9b15cf997d")
 q.execute("select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=641316");assert q.fetchone()==(0,)
 q.execute("select STATUS,CUSTODY_RELEASE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID='SINGLE.FULL.LOAD:9b15cf997d'");assert q.fetchone()==("DEPARTED","INTERWARE.CUSTODY:117f1e5e26")
 print("PASS122 continued existing ordinary ST641316/current original customer64 qty3 unchanged/no second fulfillment, source-pinned actual onward load3/P0H0/event1/SAP1/replay/native depart0. Original legacy address explicit documented confirmation; initial oversized event type transaction rolled back. tag="+tag,flush=True)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_ONWARD%'and upper(SQL_TEXT) not like '%V$SQL%'and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
