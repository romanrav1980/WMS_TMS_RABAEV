import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)AVG_MS,substr(SQL_TEXT,1,140)SQL_HEAD from V$SQL
where PARSING_SCHEMA_NAME='RABAEV'and LAST_ACTIVE_TIME>sysdate-1/48
and (upper(SQL_TEXT)like 'SELECT COUNT(*)%FROM RRL_CASE_PICK_LINE%'
or upper(SQL_TEXT)like 'SELECT COUNT(*)%FROM RRL_CASE_CARRIER_LOT%'
or upper(SQL_TEXT)like 'SELECT COUNT(*)%FROM RRL_TARE_BOOK%')
and upper(SQL_TEXT)not like '%FROM V$SQL%' order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 6 rows only"""))
print(g.fetch_all("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_CASE_RETURN_CMD','RRL_WAVE_EXEC_ACCESS')"))
