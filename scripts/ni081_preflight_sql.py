import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
print(OracleGateway().fetch_all("""select substr(sql_text,1,140) sql_text,executions,
 round(elapsed_time/nullif(executions,0)/1000,3) ms from v$sql
 where (upper(sql_text)like '%JSON_TABLE(:NUMBERS%'or upper(sql_text)like 'SELECT ID,ST_NUMBER,WARE_ID,TRANSTASK_ID,CONDITION FROM RRL_SBORKA_PALLETS%'or upper(sql_text)like '%INTO PLACES%'or upper(sql_text)like '%SELECT TO_CLOB(PAYLOAD),APPLIED_AT%')
 and upper(sql_text)not like '%V$SQL%'and executions>0 order by last_active_time desc fetch first 4 rows only"""))
