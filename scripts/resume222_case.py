import sys,json
from pathlib import Path
import oracledb,httpx
from concurrent.futures import ThreadPoolExecutor
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.transport_composition import build_transport_loading
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.oracle_gateway import OracleGateway
from app.modules.inventory.contracts_stock import StockCommand
cfg=get_settings();tag="6ac14257b5";base="http://127.0.0.1:8088";ware=7096290;trip=33541;vehicle=10048;sender="TC219"+tag;driver_user="TD219"+tag;lot="FULL.QA:"+tag;shipop="SINGLE.FULL.LOAD:"+tag;bookop="TARE.FULL.BOOK:"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 q=conn.cursor();conn.call_timeout=15000
 q.execute("select PASS from RUSERS where ID=:a",a=sender);sender_api=httpx.Client(auth=(sender,q.fetchone()[0]),timeout=35)
 q.execute("select PASS from RUSERS where ID=:a",a=driver_user);driver_api=httpx.Client(auth=(driver_user,q.fetchone()[0]),timeout=35)
 q.execute("select DOCK,CONTENT_VERSION,json_value(COMPOSITION_JSON,'$.cell')from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o",o=shipop);dock,version,shipcell=q.fetchone();preview={"expected_version":version}
 q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:u",u=lot);wave=q.fetchone()[0]
 q.execute("select VODITEL_ID from RRL_TRANSPORT_TASK where ID=:t",t=trip);driver=q.fetchone()[0]
 def api(client,method,path,body=None,status=200):
  r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()


 load_id="FULL222.LOAD:"+tag
 q.execute("select u.OPERATION_ID,c.CELL_SLOT_ID,sl.SLOT_CODE from RRL_TT_UNLOAD_FACT u join RRL_RECEIPT_SLOT_CLAIM c on c.UID_PALLET=u.ROOT_UID and c.CELL=u.CELL_CODE join RRL_TOPOLOGY_CELL_SLOT sl on sl.CELL_SLOT_ID=c.CELL_SLOT_ID where u.LOAD_OPERATION_ID=:p",p=load_id);winner,slot,code=q.fetchone()
 q.execute("select c.TASK_ID,c.STATUS,c.HU_GROSS_WEIGHT_KG,c.HU_BOUNDING_VOLUME_M3,t.STATUS from RRL_RECEIPT_SLOT_CLAIM c join RRL_WAREHOUSE_TASK t on t.TASK_ID=c.TASK_ID where c.CELL_SLOT_ID=:s",s=slot);task,status,mass,volume,task_status=q.fetchone();assert(status,mass,volume,task_status)==("OCCUPIED",10,1.5,"DONE")
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:t",t=task);assert q.fetchone()[0]=="SYNCED"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select distinct CELL_SLOT_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",u=lot);assert q.fetchall()==[(slot,)]
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS222 original FULLPAL current slot required/obsolete published slot refused/late capacity rollback/native late outer rollback/concurrent one winner/replay/native+3/P3H3/current measured OCCUPIED10kg1.5m3/DONE-SYNCED/same HARD coverage/current slot/protected13520/20",load_id,slot,code,task,winner,flush=True)
 print("Own primary3/3 and measured current slot retained for next existing reload; no fabricated release",flush=True)
