import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
g=OracleGateway()
print(g.fetch_all("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_CASE_TASK_ACCESS','RRL_CASE_RESOURCE_POLICY','RRL_STOCK_POSTING_API')order by OBJECT_NAME,OBJECT_TYPE"))
print(g.fetch_all("select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME in('RRL_CASE_TASK_ACCESS','RRL_CASE_RESOURCE_POLICY','RRL_STOCK_POSTING_API')order by NAME,LINE"))
print(g.fetch_all("select TABLE_NAME from USER_TABLES where TABLE_NAME like '%MIGR%'order by TABLE_NAME"))
