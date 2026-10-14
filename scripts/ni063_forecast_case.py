import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.tare_assembly import TareAssembly
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("select WARE_ID,PICK_WAVE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1020");ware,wave=q.fetchone()
 data=TareAssembly(OracleGateway()).forecast(ware,wave,"admin")
 assert data["planned_returns_are_available"] is False and data["scope"]=="EXISTING_STANDALONE_CASE"
 row=next(x for x in data["types"] if x["pallet_type_id"]==1)
 assert int(row["shortage_quantity"])==max(row["unbooked_case_count"]-int(row["available_quantity"]),0)
 with httpx.Client(auth=("admin","admin123"),timeout=20) as client:
  r=client.get(f"http://127.0.0.1:8088/api/inventory/tare/warehouses/{ware}/waves/{wave}/forecast")
  assert r.status_code==200,(r.status_code,r.text[:1200])
  assert r.json()==data
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL
 where upper(SQL_TEXT) like '%UNBOOKED_COUNT%' and upper(SQL_TEXT) not like '%V$SQL%'
 and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("PASS104 actual existing wave forecast/API, unbooked",row["unbooked_case_count"],"free",row["available_quantity"],"shortage",row["shortage_quantity"],"no write")
 print("SQL milliseconds/executions",q.fetchall())
