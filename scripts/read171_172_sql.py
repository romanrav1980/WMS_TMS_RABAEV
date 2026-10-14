import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)AVG_MS,substr(SQL_TEXT,1,140)SQL_HEAD
from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and LAST_ACTIVE_TIME>sysdate-1/48
and (upper(SQL_TEXT)like '%RRL_STOCK_POOL_READ.LINE_SNAPSHOT_JSON%'or upper(SQL_TEXT)like '%FROM RRL_PICK_WAVE_ORDER WO JOIN RRL_PICK_PLAN_LINE PL%'
or upper(SQL_TEXT)like '%INTO :B%FROM RRL_CASE_PICK_TASK%')
and upper(SQL_TEXT)not like '%FROM V$SQL%'order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 8 rows only"""))
print(g.fetch_all("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_POOL_READ','RRL_STOCK_POOL_CMD','RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_FINISH_CMD','RRL_STOCK_POSTING_API')"))
