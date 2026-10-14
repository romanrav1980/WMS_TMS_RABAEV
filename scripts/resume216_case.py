import sys,json
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.oracle_gateway import OracleGateway
s=get_settings();tag="7df96570";case=1118;wave=472;ware=38255845;load_id="SMALL216.LOAD:"+tag;actor="UL216"+tag;uri="http://127.0.0.1:8088/api/transport/loading/unload"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("update RUSERS set DELETED=0 where ID=:p_actor",p_actor=actor);c.commit()
 q.execute("select PASS from RUSERS where ID=:p_actor",p_actor=actor);secret=q.fetchone()[0]
 api=httpx.Client(auth=(actor,secret),timeout=35)
 q.execute("select CONTENT_VERSION,VEHICLE_NUMBER,DOCK,coalesce(json_value(COMPOSITION_JSON,'$.nodes[0].sscc'),ROOT_UID),json_value(COMPOSITION_JSON,'$.cell')from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id)
 version,vehicle,dock,carrier,cell=q.fetchone()
 body={"operation_id":"SMALL216.RESUME:"+tag,"load_operation_id":load_id,"expected_version":int(version),"scan_vehicle":vehicle,"scan_dock":dock,"scan_container":carrier,"scan_cell":cell,"reason":"Own216 physically unloaded before departure","target_slot_id":217,"scanned_to_slot_code":"UL216:7df96570:0"}
 canonical=StockCommand(operation_id=body["operation_id"],command_type="UNLOAD_SHIPMENT",actor=actor,source={"load_operation_id":load_id},metadata={k:v for k,v in body.items()if k not in("operation_id","load_operation_id")},lines=()).canonical_json();result=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,actor,result,None]);assert result.getvalue()is None
  q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(7,7)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_TT_UNLOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]==0
 q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]=="LOADED"
 with ThreadPoolExecutor(2)as pool:responses=list(pool.map(lambda b:api.post(uri,json=b),[body,{**body,"operation_id":body["operation_id"]+":OTHER"}]))
 assert sorted(x.status_code for x in responses)==[200,409],[(x.status_code,x.text[:1700])for x in responses]
 winner=next(x.json()for x in responses if x.status_code==200);body["operation_id"]=winner["operation_id"]
 assert api.post(uri,json=body).json()==winner
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(7,7)
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]==-7
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==7
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=actor);c.commit()
 try:
  r=api.post(uri,json=body);assert r.status_code==403,(r.status_code,r.text[:1600])
 finally:q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=actor);c.commit()
 q.execute("select count(*)from RRL_WMS_HU_LINK where LINKED_OPERATION_ID=:p_op and ACTIVE_FLAG=1",p_op=body["operation_id"]);assert q.fetchone()[0]==2
 q.execute("select count(*)from RRL_WMS_HU_LINK where UNLINKED_OPERATION_ID=:p_load and ACTIVE_FLAG=0",p_load=load_id);assert q.fetchone()[0]==2
 print("PASS216 existing CASE1118/load original-7 preserved/native late rollback/concurrent1winner/replay/current foreignWARE403/new+7/P7H7/new links2 old links2/UNLOADED/control revoked",winner["operation_id"],flush=True)

