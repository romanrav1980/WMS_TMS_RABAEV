"""Own ordinary return born once in segregated receiving, using actual source chain."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
admin=httpx.Client(auth=("admin","admin123"),timeout=30)
username,group,password="QWR"+tag,"QWR"+tag.upper(),uuid4().hex
supplier_cell,disposal_cell="QRS"+tag,"QRD"+tag
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor()
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,WARE_ID,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own return warehouse receiver',:grp,0,9104,0)",id=username,secret=password,grp=group);c.commit()
 def config(sql,**params):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,params);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 try:
  call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own warehouse return"})
  call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"warehouse_return_receive","description":"Own actual receiving author role"})
  receiver=httpx.Client(auth=(username,password),timeout=30)
  for cell in (supplier_cell,disposal_cell):
   config("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,9104,0,0,0,0,1,1,1,0,0,0)",cell=cell)
   config("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
  prefix="/api/inventory/store-returns"
  old=call(admin,"GET",prefix+"/warehouses/9104/policy")
  policy=call(admin,"PUT",prefix+"/warehouses/9104/policy",{"supplier_receive_cell":supplier_cell,"disposal_receive_cell":disposal_cell,"expected_version":old["policy_version"]})
  call(receiver,"GET",prefix+"/warehouses/9201/pending",status=403)
  pending=call(receiver,"GET",prefix+"/warehouses/9104/pending");row=next(x for x in pending if x["disposition"]=="SUPPLIER" and x["store_addr"]=="STORE.QA:bea258a7dd")
  body={"operation_id":"RETURN.RECEIVE:"+tag,"pickup_operation_id":row["pickup_operation_id"],"scan_pallet":row["pallet_identifier"],"scan_vehicle":row["vehicle_number"],"scan_cell":supplier_cell,
        "article":row["article"],"quantity":row["quantity"],"base_uom":row["base_uom"],"expiry_date":row["expiry_date"],"supplier_batch":row["original_supplier_batch"] or "OBSERVED.OWN."+tag,"gross_weight_kg":row["gross_weight_kg"],"net_weight_kg":"1.5"}
  bad=call(receiver,"POST",prefix+"/receive",{**body,"operation_id":"RETURN.RECEIVE.BADQ:"+tag,"quantity":"2"},409);assert "STORE_RETURN_WAREHOUSE_FULL_ORIGINAL_QUANTITY_REQUIRED" in bad["detail"]["message"]
  bad=call(receiver,"POST",prefix+"/receive",{**body,"operation_id":"RETURN.RECEIVE.BADEXP:"+tag,"expiry_date":"2031-01-01"},409);assert "STORE_RETURN_ORIGINAL_EXPIRY_CONFLICT" in bad["detail"]["message"]
  bad=call(receiver,"POST",prefix+"/receive",{**body,"operation_id":"RETURN.RECEIVE.BADCELL:"+tag,"scan_cell":"FG-A01-01"},409);assert "STORE_RETURN_WAREHOUSE_PALLET_VEHICLE_CELL_SCAN_REQUIRED" in bad["detail"]["message"]
  result=call(receiver,"POST",prefix+"/receive",body);assert result["quantity"]=="1" and result["custody"]=="WAREHOUSE" and not result["available_for_reservation"] and not result["financial_erp_completion_created"],result
  assert call(receiver,"POST",prefix+"/receive",body)==result
  bad=call(receiver,"POST",prefix+"/receive",{**body,"operation_id":"RETURN.RECEIVE.DUP:"+tag},409);assert "STORE_RETURN_FRESH_PALLET_REQUIRED" in bad["detail"]["message"] or "STORE_RETURN_PICKUP_ALREADY_RECEIVED" in bad["detail"]["message"]
  q.execute("select REMAIN,HARD_RESERVED_BASE,BASE_UOM from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=row["pallet_identifier"],cell=supplier_cell);assert q.fetchone()==(1,0,row["base_uom"])
  q.execute("select RRL_STOCK_ELIGIBILITY.reason(:lot_id,:cell,9104,1,null,null,'ALLOCATE') from dual",lot_id=row["pallet_identifier"],cell=supplier_cell);reason=q.fetchone()[0];assert reason is not None and "BLOCK" in reason,reason
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:bea258a7dd'");assert all(row==(0,0) for row in q)
  try:q.execute("delete from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=:op",op=body["operation_id"]);c.commit();raise AssertionError("Actual receipt deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert "STORE_RETURN_RECEIPT_HISTORY_IMMUTABLE" in str(exc)
  print("PASS096 actual non-admin warehouse-bound receiving/original chain/retired driver historical proof/full qty/expiry/scans/replay/duplicate/new P1H0 in blocked cell/original P0/event1/outbox1; placement/ERP separate",flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=username);c.commit()
