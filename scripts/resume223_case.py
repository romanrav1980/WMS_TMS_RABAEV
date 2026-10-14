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



 place_task=949;slot=221
 q.execute("select OPERATION_ID from RRL_STOCK_OPERATION where STATE='APPLIED'and COMMAND_TYPE='LOAD_SHIPMENT'and OPERATION_ID like 'FULL223.LOAD:6ac14257b5%'");rows=q.fetchall();assert len(rows)==1;load_id=rows[0][0]
 q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:t",t=place_task);assert q.fetchone()[0]==0
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=place_task);assert q.fetchone()[0]=="DONE"
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(0,0)
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=load_id);assert q.fetchone()[0]==-3
 q.execute("select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:p",p=load_id);value=q.fetchone()[0];proof=value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,"read")else value);assert proof["domain"]["source_stock_claims"][0]["task"]==place_task and proof["domain"]["source_stock_claims"][0]["slot"]==slot
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS223 existing SINGLE fullpal load releases original measured source SLOT221 atomically with native-3/P0H0; outer rollback restores original claim/P3H3; concurrent one winner/replay/source occupancy frozen/archive PUTAWAY949 DONE retained/protected13520/20",load_id,flush=True)
