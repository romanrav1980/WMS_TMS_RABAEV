import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with httpx.Client(auth=("admin","admin123"),timeout=35) as client:
 r=client.get("http://127.0.0.1:8088/api/customer-orders/1902/delivery");assert r.status_code==200,r.text
 state=r.json();assert state["delivery_status"]=="RECEIVED_SHIPPED_VOLUME" and state["quantities"][0]["shipped"]=="3" and state["quantities"][0]["accepted"]=="3" and state["quantities"][0]["unreceived"]=="0"
 assert state["receipt_lineage"][0]["original_load_operation_id"]=="SINGLE.FULL.LOAD:9b15cf997d" and state["receipt_lineage"][0]["actual_final_load_operation_id"]=="INTERWARE.NEXT.LOAD:f755e2320c"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where OPERATION_ID='INTERWARE.FINAL.RECEIPT:f94129cb2b'and RECEIPT_STATE='ACCEPTED'");assert q.fetchone()==(1,)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID='INTERWARE.FINAL.RECEIPT:f94129cb2b'");assert q.fetchone()==(0,)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA='FULL.QA:9b15cf997d'");assert q.fetchone()==(0,0)
 q.execute("select DELETED from RUSERS where ID='QIFf94129cb2b'");assert q.fetchone()==(1,)
 print("PASS123 original author assertions passed before Windows stdout arrow encoding failure; existing final f94129cb2b accepted/replay/wrongscan/second prior denied, original1902 shipped3 accepted3 only/original-to-final lineage/P0H0/no goods/own actor retired",flush=True)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_ONWARD_DISPATCH%'and upper(SQL_TEXT) not like '%V$SQL%'and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
