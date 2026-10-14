import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("""
 select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3) AVG_MS,substr(SQL_TEXT,1,240) SQL_TEXT
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT not like '%V$SQL%' and EXECUTIONS>0
 and(SQL_TEXT like '%RRL_TARE_STORE_DEBT%' and SQL_TEXT like '%OUTSTANDING%'
 or SQL_TEXT like 'INSERT INTO RRL_TARE_DELIVERY_POLICY%'
 or SQL_TEXT like 'INSERT INTO RRL_TARE_RESOLUTION%'
 or SQL_TEXT like 'INSERT INTO RRL_TARE_BOOK%'
 or SQL_TEXT like '%FROM RRL_TARE_AVAILABILITY%'
 or SQL_TEXT like 'SELECT%FROM RRL_TARE_STORE_DEBT%'
 or SQL_TEXT like 'SELECT%FROM RRL_TARE_RETURN_POLICY%')
 order by ELAPSED_TIME desc fetch first 6 rows only
 """)
 for row in q:print(json.dumps(row,ensure_ascii=True))
