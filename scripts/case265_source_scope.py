exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from app.modules.fulfillment.application.ports import StoreOrderConflict
import httpx
data=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));actor=data["actor"];ware=data["ware"];order=data["held"]["customer_order_id"]
svc=StoreOrders(OracleGateway());prep=LegacyPreparation(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,USER_GROUP from RUSERS where ID=:actor",actor=actor);secret,group=q.fetchone()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 meta("update RUSERS set DELETED=0,WARE_ID=:w where ID=:actor",w=ware,actor=actor)
 for permission in ["customer_order_view","customer_order_import","sap_store_order_import"]:
  q.execute("select count(*)from RIGHTS where USER_GROUP=:g and RIGHT1=:p",g=group,p=permission)
  if q.fetchone()[0]==0:meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,:p)",g=group,p=permission)
 try:
  detail=svc.get(order,actor);assert detail["consistent_snapshot"]and detail["source_ware_id"]==ware and detail["admission_status"]=="PENDING_CALENDAR"
  assert detail["demand_json"]["Lines"][0]["quantity"]=="1"
  assert all(x["ware_id"]==ware for x in svc.list(None,200,actor))
  assert svc.receive(data["raw_closed"].encode(),actor)["customer_order_id"]==order
  try:prep.prepare(order,{},actor)
  except StoreOrderConflict:pass
  else:raise AssertionError("Held source prepare bypass")
  q.callproc("RRL_STORE_ORDER_SCOPE.begin_source",[actor,"customer_order_import",ware])
  q.execute("begin RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);end;")
  q.callproc("RRL_STORE_ORDER_SCOPE.end_source");c.rollback()
  with httpx.Client(auth=(actor,secret),timeout=30)as client:
   url="http://127.0.0.1:8088/api/integrations/sap/store-orders"
   r=client.get(url+"/"+str(order));assert r.status_code==200 and r.json()["consistent_snapshot"],(r.status_code,r.text[:500])
   assert client.get(url,params={"warehouse_id":6667491}).status_code==403
   assert client.post(url+"/"+str(order)+"/prepare-st",json={"operation_id":"SCOPE265."+data["tag"],"pallets":[{"pallet_number":"1","lines":[{"articul":data["article"],"quantity":"1"}]}]}).status_code in {409,422}
  meta("update RUSERS set WARE_ID=6667491 where ID=:actor",actor=actor)
  for action in [lambda:svc.get(order,actor),lambda:svc.receive(data["raw_closed"].encode(),actor),lambda:prep.prepare(order,{},actor)]:
   try:action()
   except PermissionError:pass
   else:raise AssertionError("Changedware old source or cachedmessage exposed")
  meta("update RUSERS set WARE_ID=:w where ID=:actor",w=ware,actor=actor)
  meta("delete from RIGHTS where USER_GROUP=:g and RIGHT1='customer_order_view'",g=group)
  try:svc.get(order,actor)
  except PermissionError:pass
  else:raise AssertionError("Revoked source read")
  q.execute("select count(*)from RRL_SAP_STORE_ORDER");assert q.fetchone()==(2,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like 'select s.*,c.WARE_ID SOURCE_WARE_ID,%'or sql_text like 'select s.CUSTOMER_ORDER_ID,s.SENDER,s.ORDER_NUMBER,%'order by last_active_time desc fetch first 4 rows only");print("SQL_MS",q.fetchall())
 finally:
  q.callproc("RRL_STORE_ORDER_SCOPE.end_source");c.rollback()
  meta("update RUSERS set DELETED=1 where ID=:actor",actor=actor)
print("PASS265 sameown264sources/currentWARE list-detail snapshot/nativeJSON/ERP cachedsource/heldprep/currentrights sharedCFG4/no stock writecontext/foreignfilterHTTP403/currentHTTP200/changedWARE cachedread-import-prepare denied/revokedview/actorretired/sourcecount2/protected20-20/no birth")
