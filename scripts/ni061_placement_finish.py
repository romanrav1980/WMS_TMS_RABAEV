import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();tag="b69f937895";task=829;lot="FULL.QA:9b15cf997d";target="QIOec6052b26e";source="QIR349bc1ff57"
 body={"operation_id":"INTERWARE.PUT.COMPLETE:"+tag,"scanned_pallet":lot,"scanned_from_cell":source,"scanned_to_cell":target,"fact_qty":"3"}
 with httpx.Client(auth=("admin","admin123"),timeout=35) as client:
  url=f"http://127.0.0.1:8088/api/warehouse-tasks/{task}/complete";r=client.post(url,json=body);assert r.status_code==200,(r.status_code,r.text[:2400]);done=r.json();assert done["result"]["status"]=="DONE"
  assert client.post(url,json=body).json()==done
 q.execute("select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id order by CELL",lot_id=lot);stock=q.fetchall();assert sum(x[1]for x in stock)==3 and sum(x[2]for x in stock)==0 and next(x[1]for x in stock if x[0]==target)==3,stock
 q.execute("select TASK_ID,ROOT_UID,BASE_QTY,BASE_UOM from RRL_INTERWARE_PLACEMENT where RECEIPT_OPERATION_ID='INTERWARE.RECEIVE:349bc1ff57'");assert q.fetchone()==(task,lot,3,"EA")
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:task",task=task);assert q.fetchone()==("SYNCED",)
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,3)
 print("PASS120 continued original task829 DONE/SYNCED/replay/sumP3H0/receiving0/outbound3/immutable original119 placement, wrong scan and second plan prior denied. TaskRoot guard uses actual canonical source.task_id; initial failure rolled back. tag="+tag,flush=True)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
