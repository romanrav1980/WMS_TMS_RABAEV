import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select substr(sql_text,1,130)sql_text,executions,round(elapsed_time/nullif(executions,0)/1000,3)ms from v$sql
 where (upper(sql_text)like '%SELECT WARE_ID%RRL_CASE_PICK_TASK%CASE_PICK_TASK_ID%'
 or upper(sql_text)like '%SELECT WARE_ID,USER_GROUP%RUSERS%ID=%')
 and upper(sql_text)not like '%V$SQL%'and executions>0 order by last_active_time desc fetch first 3 rows only"""))
print(g.fetch_all("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-10-165-case-current-warehouse'"))
