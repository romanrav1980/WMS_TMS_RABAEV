"""Existing warehouse task completes ordinary return in blocked target, no duplicate engine."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
client=httpx.Client(auth=("admin","admin123"),timeout=30)
def call(method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor()
 q.execute("""
 select r.OPERATION_ID,r.UID_PALLET,r.RECEIVE_CELL,r.BASE_QTY,r.BASE_UOM,r.NAKLAD_ID
 from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=r.APPROVAL_OPERATION_ID
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd'
 """);receipt,lot,source,quantity,uom,naklad=q.fetchone()
 targets=["QRPS"+tag,"QRPD"+tag]
 def config(sql,**params):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,params);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 for cell in targets:
  config("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,9104,0,0,0,0,1,1,1,0,10,0)",cell=cell)
  config("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 old=call("GET","/api/inventory/store-returns/warehouses/9104/policy")
 prefix="/api/inventory/store-return-putaway"
 policy=call("PUT",prefix+"/warehouses/9104/targets",{"supplier_target_cell":targets[0],"disposal_target_cell":targets[1],"expected_version":old["policy_version"]})
 rows=call("GET",prefix+"/warehouses/9104/pending");assert any(x["receipt_operation_id"]==receipt for x in rows)
 plan={"operation_id":"RETURN.PUT.PLAN:"+tag,"receipt_operation_id":receipt}
 created=call("POST",prefix+"/plan",plan);task=created["task_id"];assert created["quantity"]=="1" and not created["warehouse_stock_changed"]
 assert call("POST",prefix+"/plan",plan)==created
 bad=call("POST",prefix+"/plan",{**plan,"operation_id":"RETURN.PUT.DUP:"+tag},409);assert "STORE_RETURN_EXISTING_ACTIVE_PLACEMENT_TASK" in bad["detail"]["message"]
 taskpath="/api/warehouse-tasks/"+str(task)
 call("POST",taskpath+"/assign",{"assigned_to":"admin"})
 call("POST",taskpath+"/start",{})
 completion={"operation_id":"RETURN.PUT.COMPLETE:"+tag,"scanned_pallet":lot,"scanned_from_cell":source,"scanned_to_cell":targets[0],"fact_qty":"1"}
 bad=call("POST",taskpath+"/complete",{**completion,"operation_id":"RETURN.PUT.BADSCAN:"+tag,"scanned_to_cell":"FOREIGN"},409)
 done=call("POST",taskpath+"/complete",completion);assert done["result"]["status"]=="DONE" and done["result"]["pallet_identifier"]==lot,done
 assert call("POST",taskpath+"/complete",completion)==done
 q.execute("select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id order by CELL",lot_id=lot);stock=q.fetchall();assert sum(x[1] for x in stock)==1 and sum(x[2] for x in stock)==0 and next(x for x in stock if x[0]==targets[0])[1]==1,stock
 q.execute("select TASK_ID,TARGET_CELL,BASE_QTY,BASE_UOM from RRL_STORE_RETURN_PLACEMENT where RECEIPT_OPERATION_ID=:receipt",receipt=receipt);assert q.fetchone()==(task,targets[0],1,uom)
 q.execute("select CONDITION from RRL_PRIHOD_NAKLAD where ID=:id",id=naklad);assert q.fetchone()==(2,)
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:task",task=task);assert q.fetchone()==("SYNCED",)
 q.execute("select count(*) from RRL_SAP_RECEIPT_OUTBOX where EVENT_ID=:event and EVENT_TYPE='STORE_RETURN_PLACED' and STATUS='PENDING'",event="STORE_RETURN_PLACED:"+str(task));assert q.fetchone()==(1,)
 q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=completion["operation_id"]);assert q.fetchone()==(1,)
 q.execute("select RRL_STOCK_ELIGIBILITY.reason(:lot_id,:cell,9104,1,null,null,'ALLOCATE') from dual",lot_id=lot,cell=targets[0]);assert "BLOCK" in q.fetchone()[0]
 try:q.execute("delete from RRL_STORE_RETURN_PLACEMENT where RECEIPT_OPERATION_ID=:receipt",receipt=receipt);c.commit();raise AssertionError("Placement deleted")
 except oracledb.DatabaseError as exc:c.rollback();assert "STORE_RETURN_PLACEMENT_HISTORY_IMMUTABLE" in str(exc)
 print("PASS097 existing task plan/assign/start/complete/DONE/SYNCED/source scan/replay/P total1H0 blocked target/immutable placement/typed document2/ERP outbox1+common outbox1; no second task engine",flush=True)
