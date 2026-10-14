import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
from app.modules.transport.public import assign_sts
from app.modules.inventory.public import StockCommand,StockPostingError,build_stock_posting_service
s=get_settings();tag="f877bb1524";inn=str(9940000000+int(tag[:6],16)%10000000);base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def api(method,path,body=None,status=200):
 r=admin.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();receipt="RETURN.RECEIVE:f87a0fd042"
 q.execute("select r.UID_PALLET,r.BASE_QTY,r.BASE_UOM,r.WARE_ID,p.TARGET_CELL from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_PLACEMENT p on p.RECEIPT_OPERATION_ID=r.OPERATION_ID where r.OPERATION_ID=:op",op=receipt);lot,qty,uom,ware,cell=q.fetchone();assert qty==1
 def config(sql,**params):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,params);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")

 body={"operation_id":"SUP.PREPARE:"+tag,"receipt_operation_id":receipt,"supplier_inn":inn,"reason":"Own Supply Chain supplier routing decision","decision_reference":"SC:"+tag}
 prepared=api("POST","/api/inventory/supplier-returns/prepare",body)
 assert api("POST","/api/inventory/supplier-returns/prepare",body)==prepared and not prepared["stock_changed"]
 identifier=prepared["shipment_identifier"];st_id=prepared["st_id"]
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=lot,cell=cell);assert q.fetchone()==(1,0)
 q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:st_id",st_id=st_id);trip=int(q.fetchone()[0]);dock="QSD"+tag
 loading=build_transport_loading();preview=loading.preview_single(identifier)
 assert preview["root"]==lot
 posting=build_stock_posting_service()
 try:posting.post(StockCommand(operation_id="SUP.BAD.LOGICAL:"+tag,command_type="SHIP_PALLET",actor="admin",source={"pallet_identifier":identifier},lines=(),metadata={}))
 except StockPostingError as exc:assert "SUP_RETURN_ACTUAL_PHYSICAL_LOADING_REQUIRED" in str(exc.rule_reason or exc),str(exc)
 else:raise AssertionError("Logical supplier SHIP impersonated physical load")
 load_body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":cell,"loading_context":{"transport_task_id":trip,"scan_vehicle":"QS"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"2","width_m":"1","depth_m":"1","height_m":"1"}}}
 op="SUP.LOAD:"+tag
 loaded=loading.load_single(op,identifier,load_body,"admin");assert loading.load_single(op,identifier,load_body,"admin")==loaded
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=lot,cell=cell);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_STORE_RETURN_SUP_DISPATCH where OPERATION_ID=:op and UID_PALLET=:lot_id",op=op,lot_id=lot);assert q.fetchone()==(1,)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,)
 q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='SUPPLIER_RETURN_DISPATCHED' and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=op);assert q.fetchone()==(1,)
 departed=loading.depart("SUP.DEPART:"+tag,trip,"admin");assert not departed["stock_consumed_again"]
 print("PASS108 existing PALL_SPLITTER ST/row prep and assignment, exact placed supplier return1 from segregated cell, single actual load/P0H0/replay/event1/SAP pending, separate departure no second stock; tag="+tag,flush=True)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where (upper(SQL_TEXT) like '%RRL_STORE_RETURN_SUP_%' or upper(SQL_TEXT) like '%PALL_SPLITTER%')and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 4 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
