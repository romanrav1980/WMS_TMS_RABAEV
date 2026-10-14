import sys,json
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
r=g.fetch_all("select RRL_STOCK_POOL_READ.snapshot_json(:p_ware,:p_article) SNAPSHOT from dual",{'p_ware':20052672,'p_article':'QC16700CDC0EF51'})
j=json.loads(r[0]['snapshot']);print(json.dumps({'available':j['available'],'orders':j['orders']},ensure_ascii=False))
print(g.fetch_all("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3) AVG_MS
from V$SQL where SQL_TEXT like 'select ct.CASE_PICK_TASK_ID,ct.STATUS,nvl(ct.PICKED_QTY,0)%' order by LAST_ACTIVE_TIME desc fetch first 4 rows only"""))
