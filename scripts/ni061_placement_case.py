import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QIP"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body is not None else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();receipt="INTERWARE.RECEIVE:349bc1ff57"
 q.execute("select r.ROOT_UID,r.RECEIVE_CELL,r.WARE_ID,p.OUTBOUND_DOCK from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID where r.OPERATION_ID=:op",op=receipt);lot,source,ware,target=q.fetchone()
 q.execute("select count(*)from RRL_INTERWARE_PUT_PLAN where RECEIPT_OPERATION_ID=:op",op=receipt);assert q.fetchone()==(0,),"Continue original existing task after committed plan"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own interwarehouse placer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own interwarehouse placer"})
 api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":"interwarehouse_receive","description":"Own interwarehouse placer"})
 def config(sql,**params):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,params);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 config("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,0,0,0,20,0)",cell=target,ware=ware)
 config("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target)
 try:
  p="/api/inventory/interwarehouse/placement";body={"operation_id":"INTERWARE.PUT.PLAN:"+tag,"receipt_operation_id":receipt}
  plan=api(user,p,body);task=plan["task_id"];assert plan["to_cell"]==target and not plan["stock_changed"]
  assert api(user,p,body)==plan
  api(user,p,{**body,"operation_id":"INTERWARE.PUT.SECOND:"+tag},409)
  taskpath="/api/warehouse-tasks/"+str(task)
  api(admin,taskpath+"/assign",{"assigned_to":"admin"});api(admin,taskpath+"/start",{})
  complete={"operation_id":"INTERWARE.PUT.COMPLETE:"+tag,"scanned_pallet":lot,"scanned_from_cell":source,"scanned_to_cell":target,"fact_qty":"3"}
  api(admin,taskpath+"/complete",{**complete,"operation_id":"INTERWARE.PUT.BADSCAN:"+tag,"scanned_to_cell":"FOREIGN"},409)
  done=api(admin,taskpath+"/complete",complete);assert done["result"]["status"]=="DONE" and done["result"]["pallet_identifier"]==lot
  assert api(admin,taskpath+"/complete",complete)==done
  q.execute("select CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id order by CELL",lot_id=lot);stock=q.fetchall();assert sum(x[1] for x in stock)==3 and sum(x[2] for x in stock)==0 and next(x[1]for x in stock if x[0]==target)==3,stock
  q.execute("select TASK_ID,ROOT_UID,BASE_QTY,BASE_UOM from RRL_INTERWARE_PLACEMENT where RECEIPT_OPERATION_ID=:op",op=receipt);assert q.fetchone()==(task,lot,3,"EA")
  q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:task",task=task);assert q.fetchone()==("SYNCED",)
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=complete["operation_id"]);assert q.fetchone()==(1,3)
  print("PASS120 original119/native MANUAL PUTAWAY task"+str(task)+" DONE/SYNCED/replay/second plan denied/scans/source0/outbound3/sumP3H0/immutable placement/source-target journal1/no customer duplicate; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
