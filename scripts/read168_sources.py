import sys,json
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
for name,lo,hi in [('RRL_PICKING_API',50,112),('RRL_PICKING_API',327,395),('RRL_STOCK_WAVE_FINISH_CMD',1,120)]:
 print(name,lo,hi)
 print(''.join(r['text']for r in g.fetch_all("select TEXT from USER_SOURCE where NAME=:p_name and TYPE='PACKAGE BODY' and LINE between :p_lo and :p_hi order by LINE",{'p_name':name,'p_lo':lo,'p_hi':hi})))
print(g.fetch_all("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY' and NAME in('RRL_CUSTOMER_ORDER_POOL_API','RRL_PICK_WAVE_API','RRL_PICK_WAVE_META') and (upper(TEXT) like '%CANCEL%' or upper(TEXT) like '%PICK_PLAN%') order by NAME,LINE fetch first 60 rows only"))
