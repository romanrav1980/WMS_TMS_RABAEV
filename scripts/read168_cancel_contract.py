import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select LINE,TEXT from USER_SOURCE where NAME='RRL_PICKING_API'and TYPE='PACKAGE BODY'
 and(upper(TEXT)like '%PROCEDURE CANCEL_PLAN%'or upper(TEXT)like '%ALREADY%'or upper(TEXT)like '%CANCELLED%')
 order by LINE fetch first 20 rows only"""))
print(g.fetch_all("select CUSTOMER_ORDER_ID,PICK_PLAN_ID,STATUS from RRL_PICK_PLAN where PICK_PLAN_ID in(select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=402)"))
