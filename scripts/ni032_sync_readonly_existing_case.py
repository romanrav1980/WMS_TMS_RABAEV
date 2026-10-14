"""147 original120 completed task829: sync retry reads only native same-TX proof."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();op="INTERWARE.PUT.COMPLETE:b69f937895"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def snapshot():
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=op);events=q.fetchone()
  q.execute("select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:9b15cf997d'order by CELL");stock=q.fetchall()
  q.execute("select SYNC_ID,SYNC_STATUS,SYNC_ATTEMPT,SYNCED_AT,UPDATED_AT from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=829 order by SYNC_ID");return events,stock,q.fetchall()
 before=snapshot()
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  url="http://127.0.0.1:8088/api/warehouse-tasks/829/sync/retry"
  r=client.post(url,json={});assert r.status_code==200,(r.status_code,r.text[:1500]);saved=r.json()
  assert saved["sync"]["sync_status"]=="SYNCED"
  again=client.post(url,json={});assert again.status_code==200 and again.json()==saved
 assert snapshot()==before and before[0]==(1,3)
 print("PASS147 original completed829 sync retry twice exact; native SYNCED proof returned, all event/stock/sync attempts/timestamps unchanged",flush=True)
