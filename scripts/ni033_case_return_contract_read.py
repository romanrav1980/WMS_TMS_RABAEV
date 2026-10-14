import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("""select LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_RETURN_CMD'and TYPE='PACKAGE BODY'
 and(upper(TEXT)like '%RESERV%'or upper(TEXT)like '%PICKED_QTY%'or upper(TEXT)like '%SOURCE_UID%'or upper(TEXT)like '%TARGET_UID%')
 order by LINE fetch first 24 rows only"""))
