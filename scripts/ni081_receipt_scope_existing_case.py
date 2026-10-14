"""146 exercise native access adapter with actual users and rollback-only reads."""
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.infrastructure.receipt_task_access import assert_receipt_task_scope
from app.modules.inventory.api.receiving_routes import ReplanPutaway
s=get_settings()
value="LEGACY.INTERNAL.PALLET.ID.123456789012345678"
request=ReplanPutaway(operation_id="REPLAN146.VALIDATE",scanned_pallet=value,scanned_from_cell="SOURCE",reason="Own existing identifier shape")
assert request.scanned_pallet==value
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();assert_receipt_task_scope(q,829,"admin")
 try:assert_receipt_task_scope(q,829,"Q1341a19738325")
 except PermissionError as exc:assert str(exc)=="TASK_USER_WAREHOUSE_FORBIDDEN"
 else:raise AssertionError("Receipt adapter admitted foreign actor")
 c.rollback()
print("PASS146 actual scope adapter own global/foreign denied PermissionError; ReplanPutaway retains internal identifier42; no stock/task/config write",flush=True)
