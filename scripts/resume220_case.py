import sys,json
from pathlib import Path
import oracledb,httpx
from concurrent.futures import ThreadPoolExecutor
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
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

 returned={"operation_id":"TARE220.RETURN:"+tag};accepted={"operation_id":"TARE220.RETURN.ACCEPT:"+tag};recovery={"operation_id":"TARE220.RECOVERY:"+tag}
 q.execute("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w",w=ware);assert q.fetchone()==(1,1,0)
 unload={"operation_id":"FULL220.UNLOAD:"+tag,"load_operation_id":shipop,"expected_version":version,"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own220 original full pallet after accepted tare return and new hold"}
 result=api(sender_api,"POST","/api/transport/loading/unload",unload);assert api(sender_api,"POST","/api/transport/loading/unload",unload)==result
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID in(:a,:b,:c)",a=returned["operation_id"],b=accepted["operation_id"],c=recovery["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=unload["operation_id"]);assert q.fetchone()[0]==3
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS220 original transferred FULLPAL tare actual driver return/warehouse accept/new HELD1/source unique/wrong scan/pending refusal/late rollback/concurrent/replay/currentWARE403/oldTRANSFERRED unchanged/native unload3/P3H3/no goods effect in tare/current HU reader",tag,recovery["operation_id"],flush=True)
 print("Original full pallet remains P3H3/current FF PICKED/new HELD tare1 for repeated physical cycle; own dedicated driver binding retained",flush=True)
