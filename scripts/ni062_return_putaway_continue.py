import sys,json
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
import httpx,oracledb
from app.config import get_settings
cfg=get_settings()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='STORE_RETURN' and TASK_ID=823")
 task,lot,source,target=q.fetchone()
 body={"operation_id":"RETURN.PUT.COMPLETE:dab5c00141","scanned_pallet":lot,"scanned_from_cell":source,"scanned_to_cell":target,"fact_qty":"1"}
 with httpx.Client(auth=("admin","admin123"),timeout=35) as client:
  r=client.post(f"http://127.0.0.1:8088/api/warehouse-tasks/{task}/complete",json=body)
  print(r.status_code,r.text[:2400]);r.raise_for_status()
  replay=client.post(f"http://127.0.0.1:8088/api/warehouse-tasks/{task}/complete",json=body)
  assert replay.json()==r.json()
 q.execute("select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id order by CELL",lot_id=lot)
 stock=q.fetchall();assert sum(x[1] for x in stock)==1 and sum(x[2] for x in stock)==0 and next(x for x in stock if x[0]==target)[1]==1,stock
 q.execute("select TASK_ID,TARGET_CELL,BASE_QTY from RRL_STORE_RETURN_PLACEMENT where TASK_ID=:task",task=task)
 assert q.fetchone()==(task,target,1)
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:task",task=task);assert q.fetchone()==("SYNCED",)
 q.execute("select count(*) from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:event and STATUS='PENDING'",event=f"STORE_RETURN_PLACED:{task}");assert q.fetchone()==(1,)
 print("PASS097 actual existing task DONE/SYNCED, exact replay, conserved P1H0, immutable placement and pending SAP event")
