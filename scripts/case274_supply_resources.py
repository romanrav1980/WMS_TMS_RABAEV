exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.modules.platform.public import read_oracle_json
from concurrent.futures import ThreadPoolExecutor
import time,xml.etree.ElementTree as ET
data=json.loads(Path("tmp/context273.json").read_text(encoding="utf-8"));raw=data["supply_raw"].encode();root=ET.fromstring(raw);sender=root.find("Sender").text;order=root.find("OrderNumber").text;msg=root.find("MessageId").text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select SENDER,ORDER_NUMBER,WARE_ID from RRL_SAP_SUPPLY_ORDER where ORDER_ID=:order_id",order_id=json.loads(Path("tmp/context261.json").read_text(encoding="utf-8"))["order"]);other=q.fetchone()
 q.callproc("RRL_STORE_ORDER_SCOPE.begin_supply",["admin",data["ware"],sender,order,msg])
 def independent():
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as peer:
   p=peer.cursor();started=time.monotonic()
   p.callproc("RRL_STORE_ORDER_SCOPE.begin_supply",["admin",other[2],other[0],other[1],"RESOURCE274.OTHER"])
   elapsed=time.monotonic()-started;p.callproc("RRL_STORE_ORDER_SCOPE.end_source");peer.rollback();return elapsed
 with ThreadPoolExecutor(1)as pool:
  future=pool.submit(independent);elapsed=future.result(timeout=8);assert elapsed<3,elapsed
 q.callproc("RRL_STORE_ORDER_SCOPE.end_source");c.rollback()
print("INDEPENDENT_SECONDS",round(elapsed,3))
svc=SupplyOrders(OracleGateway())
with ThreadPoolExecutor(2)as pool:results=list(pool.map(lambda _:svc.receive(raw,"SAP_FILE_GATEWAY"),range(2)))
assert all(r["order_id"]==data["supply"]["order_id"]for r in results)
# Original source warehouse must be authorized even if target is the actor warehouse.
old=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));actor=old["actor"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:actor",actor=actor);group,original,deleted=q.fetchone();assert deleted==1
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:group_id,'sap_supply_import')",group_id=group)
 try:
  meta("update RUSERS set DELETED=0,WARE_ID=:ware where ID=:actor",ware=original,actor=actor)
  try:q.callproc("RRL_STORE_ORDER_SCOPE.begin_supply",[actor,original,sender,order,"RESOURCE274.FOREIGN"])
  except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20882
  else:raise AssertionError("Target-only authorization bypass")
  c.rollback()
 finally:
  meta("update RUSERS set DELETED=1,WARE_ID=:ware where ID=:actor",ware=original,actor=actor)
  meta("delete from RIGHTS where USER_GROUP=:group_id and RIGHT1='sap_supply_import'",group_id=group)
 q.execute("select PLANNED_QTY,SOURCE_QTY from RRL_SAP_SUPPLY_LINE where ORDER_ID=:order_id",order_id=data["supply"]["order_id"]);assert q.fetchone()==(1,3)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),substr(SQL_TEXT,1,120)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and SQL_TEXT not like '%V$SQL%'and executions>0
 and (SQL_TEXT like '%FROM RRL_SAP_SUPPLY_ORDER WHERE SENDER%'or SQL_TEXT like '%RRL_STORE_ORDER_SCOPE.begin_supply%')
 order by last_active_time desc fetch first 5 rows only""");print("SQL_MS",json.dumps(q.fetchall(),ensure_ascii=True))
print("PASS274 independent source not blocked by held source/concurrent same-message replay/same original quantity/native originalWARE check/actor restored/receipt document anchors/P20H20/no source births")
