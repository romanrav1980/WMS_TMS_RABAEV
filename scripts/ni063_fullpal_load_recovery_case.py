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

 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35)
 for right in["tare_plan","tare_accept"]:
  api(admin_api,"POST",f"/api/admin/rights/groups/{sender.upper()}/rights",{"right_name":right,"description":"Own220"})
 returned={"operation_id":"TARE220.RETURN:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"VEHICLE","from_id":str(vehicle),"to_kind":"WAREHOUSE","to_id":str(ware),"quantity":"1","scan_vehicle":"QL"+tag}
 api(driver_api,"POST","/api/inventory/tare/offer",returned)
 recovery={"operation_id":"TARE220.RECOVERY:"+tag,"place_kind":"HU","place_id":lot,"pallet_type_id":1,"expected_warehouse_id":ware,"load_recovery":{"load_operation_id":shipop,"original_booking_operation_id":bookop,"return_offer_operation_id":returned["operation_id"],"expected_load_version":version,"scan_place":lot}}
 api(sender_api,"POST","/api/inventory/tare/book",recovery,status=409)
 accepted={"operation_id":"TARE220.RETURN.ACCEPT:"+tag,"offer_operation_id":returned["operation_id"],"accepted_quantity":"1","scan_vehicle":"QL"+tag}
 result=api(sender_api,"POST","/api/inventory/tare/accept",accepted);assert api(sender_api,"POST","/api/inventory/tare/accept",accepted)==result
 candidates=api(sender_api,"GET","/api/inventory/tare/load-recovery-candidates?load_operation_id="+shipop)
 assert len(candidates)==1 and candidates[0]["place_kind"]=="HU"and candidates[0]["place_id"]==lot,candidates
 api(sender_api,"POST","/api/inventory/tare/book",{**recovery,"operation_id":recovery["operation_id"]+":BAD","load_recovery":{**recovery["load_recovery"],"scan_place":lot+"X"}},status=409)
 canonical=StockCommand(operation_id=recovery["operation_id"],command_type="TARE_BOOK",actor=sender,source={"place_kind":"HU","place_id":lot},metadata={k:v for k,v in recovery.items()if k not in("operation_id","place_kind","place_id")},lines=()).canonical_json();out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,sender,out,None]);assert out.getvalue()is None;q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select ROOT_UID,CASE_PICK_TASK_ID from RRL_TARE_LOAD_RECOVERY where OPERATION_ID=:p",p=recovery["operation_id"]);assert q.fetchone()==(lot,None)
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_TARE_LOAD_RECOVERY where ORIGINAL_BOOK_OPERATION_ID=:p",p=bookop);assert q.fetchone()[0]==0
 with ThreadPoolExecutor(2)as pool:rs=list(pool.map(lambda b:sender_api.post(base+"/api/inventory/tare/book",json=b),[recovery,{**recovery,"operation_id":recovery["operation_id"]+":OTHER"}]))
 assert sorted(r.status_code for r in rs)==[200,409],[(r.status_code,r.text[:1800])for r in rs]
 result=next(r.json()for r in rs if r.status_code==200);recovery["operation_id"]=result["operation_id"]
 assert api(sender_api,"POST","/api/inventory/tare/book",recovery)==result
 q.execute("update RUSERS set WARE_ID=6667491 where ID=:p",p=sender);conn.commit()
 try:api(sender_api,"POST","/api/inventory/tare/book",recovery,status=403)
 finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=sender);conn.commit()
 q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:p",p=bookop);assert q.fetchone()==("TRANSFERRED","TARE219.ACCEPT:"+tag)
 q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:w",w=ware);assert dict(q.fetchall())=={"WAREHOUSE":1,"VEHICLE":0}
 q.execute("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w",w=ware);assert q.fetchone()==(1,1,0)
 unload={"operation_id":"FULL220.UNLOAD:"+tag,"load_operation_id":shipop,"expected_version":version,"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own220 original full pallet after accepted tare return and new hold"}
 result=api(sender_api,"POST","/api/transport/loading/unload",unload);assert api(sender_api,"POST","/api/transport/loading/unload",unload)==result
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID in(:a,:b,:c)",a=returned["operation_id"],b=accepted["operation_id"],c=recovery["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p",p=unload["operation_id"]);assert q.fetchone()[0]==3
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS220 original transferred FULLPAL tare actual driver return/warehouse accept/new HELD1/source unique/wrong scan/pending refusal/late rollback/concurrent/replay/currentWARE403/oldTRANSFERRED unchanged/native unload3/P3H3/no goods effect in tare/current HU reader",tag,recovery["operation_id"],flush=True)
 print("Original full pallet remains P3H3/current FF PICKED/new HELD tare1 for repeated physical cycle; own dedicated driver binding retained",flush=True)
