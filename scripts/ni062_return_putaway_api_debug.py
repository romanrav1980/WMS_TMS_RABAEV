import sys,traceback
from pathlib import Path
from uuid import uuid4
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.store_return_receiving_composition import build_store_return_putaway
from app.oracle_gateway import OracleGateway
try:
 rows=OracleGateway().fetch_all("select r.OPERATION_ID from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=r.APPROVAL_OPERATION_ID where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd'")
 print(build_store_return_putaway().plan("RETURN.PUT.API:"+uuid4().hex[:10],rows[0]["operation_id"],"admin"))
except Exception:
 traceback.print_exc()
