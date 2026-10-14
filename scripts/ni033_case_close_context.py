import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("select CASE_PICK_TASK_ID,STATUS,CONTENT_VERSION,SHIPPED_OPERATION,CLOSED_AT,ASSIGNED_TO from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(1029,1030,1031,1032)order by CASE_PICK_TASK_ID"))
print(g.fetch_all("""select c.CASE_PICK_TASK_ID,c.STATUS,c.CONTENT_VERSION,w.WAVE_CODE from RRL_CASE_PICK_TASK c join RRL_PICK_WAVE w on w.PICK_WAVE_ID=c.PICK_WAVE_ID
 where c.STATUS='PICKED'and c.SHIPPED_OPERATION is null and exists(select 1 from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID and s.REMAIN>0)
 order by c.CASE_PICK_TASK_ID fetch first 3 rows only"""))
