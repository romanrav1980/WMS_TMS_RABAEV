import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_PICK_CMD'and TYPE='PACKAGE BODY'
 and(upper(TEXT)like '%STATUS=%'or upper(TEXT)like '%WAIT_CONTROL%'or upper(TEXT)like '%CLOSED_AT%')order by LINE fetch first 16 rows only"""))
print(g.fetch_all("select OPERATION_ID,to_clob(RESULT_JSON) RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID in('CASE.HTTP167:1035','CASE.HTTP167:1036')"))
