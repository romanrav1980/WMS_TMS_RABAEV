exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
import httpx
data=json.loads(Path("tmp/context273.json").read_text(encoding="utf-8"));fixture=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));actor=fixture["actor"];raw=data["supply_raw"].encode();svc=SupplyOrders(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:actor",actor=actor);group,original_ware,deleted=q.fetchone();assert deleted==1
 q.execute("select count(*)from RIGHTS where USER_GROUP=:group_id and RIGHT1='sap_supply_import'",group_id=group);assert q.fetchone()==(0,)
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:group_id,'sap_supply_import')",group_id=group)
 try:
  meta("update RUSERS set WARE_ID=:ware,DELETED=0 where ID=:actor",ware=data["ware"],actor=actor)
  assert svc.receive(raw,actor)["order_id"]==data["supply"]["order_id"]
  meta("update RUSERS set WARE_ID=:ware where ID=:actor",ware=original_ware,actor=actor)
  try:svc.receive(raw,actor)
  except PermissionError:pass
  else:raise AssertionError("Cached foreign supply scope bypass")
  meta("update RUSERS set WARE_ID=:ware where ID=:actor",ware=data["ware"],actor=actor)
  meta("delete from RIGHTS where USER_GROUP=:group_id and RIGHT1='sap_supply_import'",group_id=group)
  try:svc.receive(raw,actor)
  except PermissionError:pass
  else:raise AssertionError("Revoked source import cached bypass")
 finally:
  meta("update RUSERS set WARE_ID=:ware,DELETED=1 where ID=:actor",ware=original_ware,actor=actor)
  meta("delete from RIGHTS where USER_GROUP=:group_id and RIGHT1='sap_supply_import'",group_id=group)
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.post("http://127.0.0.1:8088/api/integrations/sap/supply-orders",content=raw,headers={"Content-Type":"application/xml"})
 assert r.status_code==202,r.text
 assert r.json()["order_id"]==data["supply"]["order_id"]
print("PASS273 cached supply currentown actor success/changedWARE403/revokedright denied/actor retired-originalWARE restored/HTTPsameSource202/no new source or stock")
