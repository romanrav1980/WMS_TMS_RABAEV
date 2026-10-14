import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timedelta,timezone
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QIW"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();source="SINGLE.FULL.LOAD:9b15cf997d";target=9104
 q.execute("select WARE_ID,ROOT_UID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=source);ware,lot=q.fetchone()
 q.execute("select count(*)from RRL_INTERWARE_PLAN where SOURCE_LOAD_OPERATION_ID=:op",op=source);assert q.fetchone()==(0,),"Use existing-case continuation after committed plan"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own interwarehouse dispatcher',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own two-leg dispatcher"})
 for right in ["transport_dispatch_edit","transport_dispatch_view"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own two-leg dispatcher"})
 def config(sql,**params):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,params);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select min(TRANSPORTTYPE)from RRL_TRANSPORT_TYPE");typ=q.fetchone()[0]
 q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
 vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QI"+tag,typ,20,4,0,None]));c.commit()
 q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=int(q.fetchone()[0]);inbound="QII"+tag;outbound="QIO"+tag
 for dock in [inbound,outbound]:config("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock,ware=target)
 config("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",id=trip,plate="QI"+tag,typ=typ,driver=driver,dock=outbound)
 config("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
 try:
  now=datetime.now(timezone.utc);body={"operation_id":"INTERWARE.PLAN:"+tag,"source_load_operation_id":source,"target_warehouse_id":target,"target_trip_id":trip,"inbound_dock":inbound,"arrival_due":(now+timedelta(hours=1)).isoformat(),"ready_due":(now+timedelta(hours=2)).isoformat(),"reason":"Own ordinary two-leg software fixture","decision_reference":"IW:"+tag}
  p="/api/inventory/interwarehouse"
  api(user,p+"/plan",{**body,"operation_id":"INTERWARE.BAD:"+tag,"target_warehouse_id":ware},409)
  result=api(user,p+"/plan",body);assert result["status"]=="PLANNED" and not result["stock_changed"] and not result["physical_receipt_confirmed"]
  assert api(user,p+"/plan",body)==result
  api(user,p+"/plan",{**body,"reason":"Changed"},409)
  api(admin,p+"/plan",{**body,"operation_id":"INTERWARE.SECOND:"+tag},409)
  api(user,p+f"/warehouses/{target}",status=403)
  assert any(x["operation_id"]==body["operation_id"] for x in api(admin,p+f"/warehouses/{target}"))
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(0,)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=lot);assert q.fetchone()==(0,0)
  q.execute("select count(*)from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and ACTIVE_FLAG=1",op=source);assert q.fetchone()==(1,)
  print("PASS118 original departed ordinary source/existing outbound trip, current source-bound dispatcher/target queue/foreign403/replay/conflict/second409, no stock effect or new ST; tag="+tag+" trip="+str(trip),flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_PLAN%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
