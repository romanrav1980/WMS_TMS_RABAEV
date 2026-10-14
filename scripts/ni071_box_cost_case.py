import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def api(path,body=None,status=200):
 r=admin.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();trip=33514;ware=2378876;p="/api/finance/logistics-costs"
 q.execute("select PRICE,PAY_ORDER_ID from RRL_TRANSPORT_TASK where ID=:id",id=trip);before=q.fetchone()
 q.execute("select count(*)from RRL_EVENTS");events_before=q.fetchone()[0]
 rate={"warehouse_id":ware,"currency":"GEL","rate":"2.50","effective_from":"2026-01-01","expected_version":0,"reason":"Own original warehouse BOX norm, common work included","decision_reference":"FIN:"+tag}
 registered=api(p+"/rates",rate);assert registered["version"]==1
 body={"operation_id":"COST.BOX:"+tag,"trip_id":trip,"warehouse_id":ware,"currency":"GEL"}
 result=api(p+"/calculate",body);assert result["amount"]=="2.50" and result["lines"][0]["quantity"]==1 and result["lines"][0]["version"]==1
 assert api(p+"/calculate",body)==result
 api(p+"/calculate",{**body,"currency":"USD"},409)
 api(p+"/calculate",{**body,"operation_id":"COST.SECOND:"+tag},409)
 changed=api(p+"/rates",{**rate,"rate":"9.00","effective_from":"2027-01-01","expected_version":1,"decision_reference":"FUTURE:"+tag});assert changed["version"]==2
 assert api(p+"/calculate",body)==result
 detail=api(p+f"/trips/{trip}");assert detail["lines"][0]["amount"]=="2.5" and detail["lines"][0]["version_no"]==1
 q.execute("select PRICE,PAY_ORDER_ID from RRL_TRANSPORT_TASK where ID=:id",id=trip);assert q.fetchone()==before
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==events_before
 print("PASS111 actual original departed physical BOX1/immutable rate2.50 GEL/charge2.50/frozen v1 despite future9.00 v2/replay/conflict/second denied/original transport PRICE and goods journal unchanged; tag="+tag,flush=True)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_LOGISTICS_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
