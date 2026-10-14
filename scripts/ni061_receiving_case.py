import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QIR"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();plan="INTERWARE.PLAN:ec6052b26e"
 q.execute("select p.TARGET_WARE_ID,p.ROOT_UID,p.INBOUND_DOCK,t.TRANSPORT,lot.ARTICUL,a.BARCODE_SHT from RRL_INTERWARE_PLAN p join RRL_TRANSPORT_TASK t on t.ID=p.SOURCE_TT_ID join RRL_PALLETS lot on lot.UID_PALLET=p.ROOT_UID join RRL_ARTICULS a on a.ACTICUL=lot.ARTICUL where p.OPERATION_ID=:op",op=plan);ware,lot,dock,vehicle,article,barcode=q.fetchone()
 q.execute("select count(*)from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=:op",op=plan);assert q.fetchone()==(0,),"Continue existing committed receipt instead"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own interwarehouse receiver',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own interwarehouse receiver"})
 for right in ["interwarehouse_receive","transport_dispatch_view"]:api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own interwarehouse receiver"})
 def config(sql,**params):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,params);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 cell="QIR"+tag
 config("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,1,1,0,100,0)",cell=cell,ware=ware)
 config("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 try:
  p="/api/inventory/interwarehouse"
  receive={"operation_id":"INTERWARE.RECEIVE:"+tag,"plan_operation_id":plan,"scan_pallet":lot,"scan_cell":cell,"scan_article":barcode,"article":article,"quantity":"3","base_uom":"EA"}
  api(user,p+"/receive",{**receive,"operation_id":"INTERWARE.EARLY:"+tag},409)
  unload={"operation_id":"INTERWARE.UNLOAD:"+tag,"plan_operation_id":plan,"scan_pallet":lot,"scan_vehicle":vehicle,"scan_dock":dock}
  api(user,p+"/unload",{**unload,"operation_id":"INTERWARE.BADSCAN:"+tag,"scan_vehicle":"FOREIGN"},409)
  result=api(user,p+"/unload",unload);assert result["status"]=="UNLOADED_PENDING_RECEIPT" and not result["stock_changed"]
  assert api(user,p+"/unload",unload)==result
  api(user,p+"/unload",{**unload,"operation_id":"INTERWARE.UNLOADSECOND:"+tag},409)
  api(user,p+"/receive",{**receive,"operation_id":"INTERWARE.BADQ:"+tag,"quantity":"2"},409)
  config("update RUSERS set WARE_ID=:ware where ID=:id",ware=2378876,id=actor)
  api(user,p+"/receive",receive,403)
  config("update RUSERS set WARE_ID=:ware where ID=:id",ware=ware,id=actor)
  result=api(user,p+"/receive",receive);assert result["status"]=="RECEIVED_PENDING_PLACEMENT" and result["quantity"]=="3" and not result["customer_fulfillment_repeated"]
  assert api(user,p+"/receive",receive)==result
  api(user,p+"/receive",{**receive,"quantity":"2"},409)
  api(user,p+"/receive",{**receive,"operation_id":"INTERWARE.SECONDRECEIVE:"+tag},409)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=lot,cell=cell);assert q.fetchone()==(3,0)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id and CELL!=:cell",lot_id=lot,cell=cell);assert q.fetchone()==(0,0)
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=receive["operation_id"]);assert q.fetchone()==(1,3)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=unload["operation_id"]);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='INTERWAREHOUSE_RECEIVED' and json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=receive["operation_id"]);assert q.fetchone()==(1,)
  assert any(x["receipt_operation_id"]==receive["operation_id"] for x in api(user,p+f"/warehouses/{ware}"))
  print("PASS119 original118 actual unload0/target receipt3H0/native sole core/event1/SAP1/old source0/original ST retained/replay/conflict/second/early/wrong scan/foreign denied; tag="+tag+" cell="+cell,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
