import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select i.INDEX_NAME,i.STATUS,c.COLUMN_NAME,c.COLUMN_POSITION from USER_INDEXES i
 join USER_IND_COLUMNS c on c.INDEX_NAME=i.INDEX_NAME where i.TABLE_NAME='RRL_SBORKA_PALLETS'
 order by i.INDEX_NAME,c.COLUMN_POSITION"""))
rows=g.fetch_all("""select SQL_ID,CHILD_NUMBER from v$sql where upper(sql_text)like 'SELECT P.ID,P.ST_NUMBER,P.WARE_ID,P.TRANSTASK_ID,P.CONDITION%JSON_TABLE(:NUMBERS%'order by last_active_time desc fetch first 1 rows only""")
if rows:
 print(g.fetch_all("select PLAN_TABLE_OUTPUT from table(dbms_xplan.display_cursor(:sqlid,:child,'BASIC'))",{"sqlid":rows[0]["sql_id"],"child":rows[0]["child_number"]}))
