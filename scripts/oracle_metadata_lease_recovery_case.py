"""A failed admission must not poison the next independent Oracle metadata lease."""
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
gateway=OracleGateway()
try:
 with gateway.transaction("Own failed metadata admission") as cursor:
  cursor.execute("select sys_context('USERENV','SID') from dual");first_sid=cursor.fetchone()[0]
  cursor.execute("begin RRL_STOCK_LOCK_API.begin_plan;raise_application_error(-20899,'OWN_METADATA_ADMISSION_FAILURE');end;")
except oracledb.DatabaseError as exc:
 assert "OWN_METADATA_ADMISSION_FAILURE" in str(exc),str(exc)
else:raise AssertionError("Controlled admission failure did not occur")
with gateway.transaction("Own metadata admission after failed lease") as cursor:
 cursor.execute("select sys_context('USERENV','SID') from dual");assert cursor.fetchone()[0]==first_sid
 cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change('admin','pick_wave_launch');end;")
 cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
print("PASS same actual Oracle session after failed plan admits next independent metadata transaction; no stock/domain writes",flush=True)
