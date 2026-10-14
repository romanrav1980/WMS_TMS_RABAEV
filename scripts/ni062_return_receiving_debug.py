"""Rollback-only changed command diagnostic, no history/stock commit."""
import sys,json
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.infrastructure.store_return_receiving import StoreReturnReceiving
from app.oracle_gateway import OracleGateway
cfg=get_settings();service=StoreReturnReceiving(OracleGateway(),lambda *args: {})
row=next(x for x in service.pending(9104,"admin") if x["store_addr"]=="STORE.QA:bea258a7dd")
payload={"contract_version":2,"operation_id":"RETURN.DEBUG:"+uuid4().hex,"command_type":"STORE_RETURN_RECEIVE","actor":"admin","source":{"pickup_operation_id":row["pickup_operation_id"]},"lines":[],"units":[],
 "metadata":{"scan_pallet":row["pallet_identifier"],"scan_vehicle":row["vehicle_number"],"scan_cell":row["receive_cell"],"article":row["article"],"quantity":row["quantity"],"base_uom":row["base_uom"],"expiry_date":row["expiry_date"],"supplier_batch":"OBSERVED.QA","gross_weight_kg":row["gross_weight_kg"],"net_weight_kg":"1.5"}}
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor();inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(payload))
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
  if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  print("ROLLBACK diagnostic succeeded")
 except oracledb.DatabaseError as exc:print(str(exc),flush=True)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
