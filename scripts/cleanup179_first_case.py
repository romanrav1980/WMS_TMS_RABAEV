import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();uid="WEIGHT179:22d485ca";cell="Q167S00cdc0ef51"
 q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);v=q.fetchone()[0]
 q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:p_cell and STOCK_STATUS='AVAILABLE'",p_uid=uid,p_cell=cell);keys=[r[0]for r in q.fetchall()]
 StockPosting().post(StockCommand(operation_id="WEIGHT179.CLEAN:22d485ca",command_type="INVENTORY_COUNT",actor="admin",source={"revision_id":233},metadata={"reason":"Native cleanup after author query column correction","counts":[{"uid":uid,"cell":cell,"article":"QW17922D485CA","unit":"KG","quantity":"0","expected_stock_version":int(v),"unit_keys":keys}]},lines=()))
 print("First179 fixture cleaned by native count")
