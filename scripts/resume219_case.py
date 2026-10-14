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
 offer={"operation_id":"TARE219.OFFER:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"WAREHOUSE","from_id":str(ware),"to_kind":"VEHICLE","to_id":str(vehicle),"quantity":"1","scan_vehicle":"QL"+tag,"booking_operation_ids":[bookop]}
 unload={"operation_id":"TARE219.UNLOAD:"+tag,"load_operation_id":shipop,"expected_version":preview["expected_version"],"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own219 before acceptance"}
 cancel={"operation_id":"TARE219.CANCEL:"+tag,"offer_operation_id":offer["operation_id"],"scan_vehicle":"QL"+tag,"reason":"Own219 original sender cancels before driver accepts"}
 try:
  canonical=StockCommand(operation_id=cancel["operation_id"],command_type="TARE_OFFER_CANCEL",actor=sender,source={"offer_operation_id":offer["operation_id"]},metadata={k:v for k,v in cancel.items()if k not in("operation_id","offer_operation_id")},lines=()).canonical_json();out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,sender,out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*)from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=:p",p=offer["operation_id"]);assert q.fetchone()[0]==1
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=:p",p=offer["operation_id"]);assert q.fetchone()[0]==0
  with ThreadPoolExecutor(2)as pool:rs=list(pool.map(lambda b:sender_api.post(base+"/api/inventory/tare/offer-cancel",json=b),[cancel,{**cancel,"operation_id":cancel["operation_id"]+":OTHER"}]))
  assert sorted(r.status_code for r in rs)==[200,409],[(r.status_code,r.text[:1500])for r in rs]
  result=next(r.json()for r in rs if r.status_code==200);cancel["operation_id"]=result["operation_id"];assert api(sender_api,"POST","/api/inventory/tare/offer-cancel",cancel)==result
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p",p=sender);conn.commit()
  try:api(sender_api,"POST","/api/inventory/tare/offer-cancel",cancel,status=403)
  finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=sender);conn.commit()
  old_accept={"operation_id":"TARE219.OLD.ACCEPT:"+tag,"offer_operation_id":offer["operation_id"],"accepted_quantity":"1","scan_vehicle":"QL"+tag}
  api(driver_api,"POST","/api/inventory/tare/accept",old_accept,status=409)
  q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:p",p=bookop);assert q.fetchone()[0]=="HELD"
  q.execute("select QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:w and CUSTODIAN_KIND='WAREHOUSE'",w=ware);assert q.fetchone()[0]==1
  # Native rollback proves cancelled association no longer blocks original unloading.
  doc=StockCommand(operation_id=unload["operation_id"],command_type="UNLOAD_SHIPMENT",actor=sender,source={"load_operation_id":shipop},metadata={k:v for k,v in unload.items()if k not in("operation_id","load_operation_id")},lines=()).canonical_json()
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[doc,sender,out,None]);q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out]);q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  # Existing sender can re-offer same HELD book after explicit cancellation.
  new_offer={**offer,"operation_id":"TARE219.REOFFER:"+tag};api(sender_api,"POST","/api/inventory/tare/offer",new_offer)
  accepted={**old_accept,"operation_id":"TARE219.ACCEPT:"+tag,"offer_operation_id":new_offer["operation_id"]};api(driver_api,"POST","/api/inventory/tare/accept",accepted)
  api(sender_api,"POST","/api/inventory/tare/offer-cancel",{**cancel,"operation_id":"TARE219.NO.CANCEL:"+tag,"offer_operation_id":new_offer["operation_id"]},status=409)
  history=api(sender_api,"GET",f"/api/inventory/tare/trips/{trip}/offers");assert any(r["operation_id"]==offer["operation_id"]and r["cancel_operation_id"]==cancel["operation_id"]for r in history)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=cancel["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:p",p=bookop);assert q.fetchone()==("TRANSFERRED",accepted["operation_id"])
  print("PASS219 cancelled original pending handover preserves offer/book/balance; rollback/concurrent/replay/currentWARE403/no old accept/unload rollback3/3/reoffer actual accepted, transferred FULLPAL preserved for recovery",tag,ware,wave,lot,shipop,bookop,sender,driver_user,driver,trip,flush=True)
 finally:
  conn.rollback();q.callproc('RRL_STOCK_POSTING_API.reset_connection')
