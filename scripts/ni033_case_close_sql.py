import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select substr(sql_text,1,140)sql_text,executions,round(elapsed_time/nullif(executions,0)/1000,3)ms from v$sql
 where (upper(sql_text)like '%LEFT JOIN(SELECT H.CASE_PICK_LINE_ID,SUM(S.REMAIN)%'
 or upper(sql_text)like '%SELECT CASE_PICK_TASK_ID,EVENT_TYPE,CREATED_BY,TO_CLOB(PAYLOAD_JSON)%'
 or upper(sql_text)like '%SELECT STATUS,NVL(CONTENT_VERSION,0),ASSIGNED_TO,SHIPPED_OPERATION%')
 and upper(sql_text)not like '%V$SQL%'and executions>0 order by last_active_time desc fetch first 3 rows only"""))
print(g.fetch_all("select PICK_WAVE_ID,WARE_ID,STATUS from RRL_PICK_WAVE where WARE_ID=20052672 order by PICK_WAVE_ID"))
