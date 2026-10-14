import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings();tag="13508027ed";actor="TR226"+tag;uid="FULL.QA:"+tag;receipt="IW226.RECEIVE:"+tag+"0"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000;q.execute("select PASS from RUSERS where ID=:a",a=actor);secret=q.fetchone()[0]
 client=httpx.Client(auth=(actor,secret),timeout=35);admin=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(h,method,path,body=None,status=200):
  r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
 api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":"warehouse_task_execute","description":"Own227 original marked placement"})
 body={"operation_id":"IW227.PLAN:"+tag,"receipt_operation_id":receipt}
 plan=api(client,"POST","/api/inventory/interwarehouse/placement",body);assert api(client,"POST","/api/inventory/interwarehouse/placement",body)==plan;task=plan["task_id"]
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:a",a=actor);c.commit()
 try:api(client,"POST","/api/inventory/interwarehouse/placement",body,403)
 finally:q.execute("update RUSERS set WARE_ID=51365792 where ID=:a",a=actor);c.commit()
 metadata={"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":plan["from_cell"],"scanned_to_cell":plan["to_cell"]}
 metadata.update(json.loads(Path("tmp/resource227.json").read_text(encoding="utf-8")))
 command={"contract_version":2,"operation_id":"IW227.ROLLBACK:"+tag,"command_type":"TASK_COMPLETE","actor":actor,"source":{"task_id":task},"lines":[],"units":[],"metadata":metadata}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),actor,out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x=plan["to_cell"]);assert q.fetchone()==(3,0)
  q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:x and STOCK_STATUS='AVAILABLE'and UNIT_VERSION=9",u=uid,x=plan["to_cell"]);assert q.fetchone()[0]==3
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x=plan["from_cell"]);assert q.fetchone()==(3,0)
 def complete(i):
  b=dict(metadata,operation_id="IW227.COMPLETE:"+tag+str(i))
  with httpx.Client(auth=(actor,secret),timeout=35)as h:return h.post(base+f"/api/warehouse-tasks/{task}/complete",json=b),b
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(complete,[0,1]))
 assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:3000])for r,b in results]
 saved,winner=next((r.json(),b)for r,b in results if r.status_code==200)
 api(client,"POST",f"/api/warehouse-tasks/{task}/complete",winner)
 q.execute("select STATUS,SYNC_STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=task);assert q.fetchone()==("DONE","SYNCED")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x=plan["from_cell"]);assert q.fetchone()==(0,0)
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:x",u=uid,x=plan["to_cell"]);assert q.fetchone()==(3,0)
 q.execute("select count(*),sum(BASE_QTY),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:x and STOCK_STATUS='AVAILABLE'and HARD_RESERVATION_ID is null",u=uid,x=plan["to_cell"]);assert q.fetchone()==(3,3,9,9)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u",u=uid);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_INTERWARE_PLACEMENT where TASK_ID=:t",t=task);assert q.fetchone()[0]==1
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS227 original marked receipt3 -> original PUTAWAY",task,"DONE/SYNCED/source0/outbound3H0/same units3 codes6/version9/native rollback/concurrent winner/replay/current foreignWARE403/protected20/20",flush=True)
