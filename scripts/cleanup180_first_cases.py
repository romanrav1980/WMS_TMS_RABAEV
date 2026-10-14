import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.infrastructure.receiving import Receiving
from app.oracle_gateway import OracleGateway
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select t.TASK_ID,t.UID_PALLET,t.FROM_CELL,t.FROM_WARE_ID,t.TARGET_ARTICUL,r.STOCK_VERSION from RRL_WAREHOUSE_TASK t join RRL_REMAINS r on r.UID_POLETA=t.UID_PALLET and r.CELL=t.FROM_CELL where t.TASK_SOURCE='SAP_RECEIPT' and t.TARGET_ARTICUL in('QW18033BF3D9E','QW180EDA4BA85')and r.REMAIN>0")
 rows=q.fetchall()
 for task,uid,cell,ware,article,v in rows:
  Receiving(OracleGateway()).cancel(int(task),"Owned180 author fixture cleanup","admin")
  q.execute("select min(ID)from RRL_REVIZION where WARE_ID=:p_ware",p_ware=ware);revision=q.fetchone()[0]
  q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=uid);keys=[r[0]for r in q.fetchall()]
  StockPosting().post(StockCommand(operation_id="WEIGHT180.CLEAN:"+article,command_type="INVENTORY_COUNT",actor="admin",source={"revision_id":int(revision)},metadata={"reason":"Native cleanup own180 fixtures","counts":[{"uid":uid,"cell":cell,"article":article,"unit":"KG","quantity":"0","expected_stock_version":int(v),"unit_keys":keys}]},lines=()))
 print("Owned180 first cases cleaned n=",len(rows))
