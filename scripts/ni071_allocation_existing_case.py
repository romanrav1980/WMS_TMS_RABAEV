import sys
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def api(body,status=200):
 r=admin.post(base+"/api/finance/expense-allocation",json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();expense="EX.REPORT:80b1fc8567";vehicle="EX.VEH.REPORT:80b1fc8567"
 q.execute("select count(*)from RRL_EVENTS");goods=q.fetchone()[0]
 api({"operation_id":"EX.BAD.VEH.ALLOC:"+tag,"expense_operation_id":vehicle},409)
 q.execute("select OPERATION_ID from RRL_LOGISTICS_EXP_ALLOCATION where EXPENSE_OPERATION_ID=:id",id=expense);original=q.fetchone()[0];tag=original.split(":")[-1]
 body={"operation_id":original,"expense_operation_id":expense}
 result=api(body);assert result["status"]=="ALLOCATED" and result["basis"]=="WEIGHT" and result["amount"]=="10.01"
 assert sum(Decimal(x["amount"])for x in result["lines"])==Decimal("10.01") and all(Decimal(x["basis_value"])>0 for x in result["lines"])
 assert api(body)==result
 api({**body,"expense_operation_id":vehicle},409)
 api({**body,"operation_id":"EX.SECOND.ALLOC:"+tag},409)
 q.execute("select to_char(sum(AMOUNT),'TM9')from RRL_LOGISTICS_EXP_ALLOC_LINE where OPERATION_ID=:op",op=body["operation_id"]);assert Decimal(q.fetchone()[0])==Decimal("10.01")
 q.execute("select count(*)from RRL_LOGISTICS_EXP_ALLOCATION where EXPENSE_OPERATION_ID=:id",id=vehicle);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==goods
 print("PASS113 actual original112 trip extra10.01GEL/frozen departed source goods weights/exact cents/immutable allocation/replay/conflict/second denied/vehicle refused/no goods; tag="+tag,flush=True)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_LOGISTICS_EXP_ALLOC%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
