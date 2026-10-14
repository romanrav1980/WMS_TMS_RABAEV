import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
print(OracleGateway().fetch_all("""select substr(sql_text,1,140)sql_text,executions,round(elapsed_time/nullif(executions,0)/1000,3)ms from v$sql
 where (upper(sql_text)like '%SELECT L.ARTICUL,%MARKING_REQUIRED%'or upper(sql_text)like '%SELECT S.CASE_PICK_SHORT_ID,%'
 or upper(sql_text)like '%SELECT S.CASE_PICK_SHORT_ID,%CT.CASE_PICK_TASK_ID=S.CASE_PICK_TASK_ID%')
 and upper(sql_text)not like '%V$SQL%'and executions>0 order by last_active_time desc fetch first 3 rows only"""))
