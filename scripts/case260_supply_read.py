"""Current original SAP receipts; only isolated auth fixture, no inventory writes."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from uuid import uuid4
import httpx
svc=SupplyOrders(OracleGateway());tag=uuid4().hex[:10];actor="SR260"+tag;group=actor.upper();secret=uuid4().hex
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select ORDER_ID,WARE_ID,NAKLAD_ID from RRL_SAP_SUPPLY_ORDER order by ORDER_ID fetch first 1 rows only");order,ware,document=q.fetchone()
 q.execute("select ORDER_ID,WARE_ID,NAKLAD_ID from RRL_SAP_SUPPLY_ORDER where WARE_ID!=:ware order by ORDER_ID fetch first 1 rows only",ware=ware);foreign,other_ware,foreign_doc=q.fetchone()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 meta("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own SAP receipt source reader',:g,:w,0,0)",a=actor,p=secret,g=group,w=ware)
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'sap_supply_view')",g=group)
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'wms_admin_login')",g=group)
 try:
  own=svc.get(order,actor);assert own["consistent_snapshot"]and own["ware_id"]==ware
  assert svc.by_receipt_document(document,actor)==own
  visible=svc.list(None,200,actor);assert visible and all(x["ware_id"]==ware for x in visible)
  for action in [lambda:svc.get(foreign,actor),lambda:svc.by_receipt_document(foreign_doc,actor),lambda:svc.list(other_ware,100,actor)]:
   try:action()
   except PermissionError:pass
   else:raise AssertionError("Foreign source leak")
  with httpx.Client(auth=(actor,secret),timeout=30)as client:
   base="http://127.0.0.1:8088/api/integrations/sap/supply-orders"
   r=client.get(base+"/"+order);assert r.status_code==200,(r.status_code,r.text[:500]);assert r.json()["consistent_snapshot"]
   assert client.get(base+"/"+foreign).status_code==403
   assert client.get(base+"/by-receipt-document/"+str(foreign_doc)).status_code==403
   r=client.get(base);assert r.status_code==200 and all(x["ware_id"]==ware for x in r.json())
  meta("update RUSERS set WARE_ID=:w where ID=:a",w=other_ware,a=actor)
  try:svc.get(order,actor)
  except PermissionError:pass
  else:raise AssertionError("Changed warehouse leak")
  meta("update RUSERS set WARE_ID=:w where ID=:a",w=ware,a=actor)
  meta("delete from RIGHTS where USER_GROUP=:g and RIGHT1='sap_supply_view'",g=group)
  try:svc.get(order,actor)
  except PermissionError:pass
  else:raise AssertionError("Revoked read")
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like 'select l.LINE_NUMBER,l.ROW_ID,l.ARTICUL,a.NAME,%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
 finally:
  meta("update RUSERS set DELETED=1 where ID=:a",a=actor)
print("PASS260 originalsupply/currentware list/detail/document singleSnapshot/foreign403/HTTP200 currentwire/changedware/revokedright/actorretired/protected20-20/no goods mutation")
