exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.fulfillment.public import build_customer_order_read_service
from app.services.customer_order_service import CustomerOrderService
service=build_customer_order_read_service()
order=service.get(1931,"admin")
assert order["customer_order_id"]==1931 and order["rows"][0]["order_qty_exact"]=="4"
current=service.get(2133,"admin")
assert current["rows"][0]["order_qty_exact"]=="12"
rows=service.list("admin",limit=5)
assert 0<len(rows)<=5
try:service.get(987654321,"admin");raise AssertionError("Missing order accepted")
except LookupError:pass
try:service.list("QA172_KRO",limit=5);raise AssertionError("Denied actor accepted")
except PermissionError:pass
legacy=CustomerOrderService().get_customer_order(1931)
assert legacy==order
results={"historical_order":order,"current_order":current,"admin_count":len(rows),"missing_refused":True,"denied_actor":True,"legacy_compatible":True}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("""select ID,WARE_ID from RUSERS where nvl(DELETED,0)=0
 and upper(trim(USER_GROUP))!='GLOBAL_ADMIN' and WARE_ID>0
 and RRL_HAS_WRIGHT(ID,'customer_order_view')=1
 order by ID fetch first 10 rows only""")
 candidates=q.fetchall();results["scoped_candidates"]=[list(x)for x in candidates]
 for actor,ware in candidates:
  q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where WARE_ID=:w order by CUSTOMER_ORDER_ID desc fetch first 1 rows only",w=ware)
  own=q.fetchone()
  q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where WARE_ID!=:w and WARE_ID>0 order by CUSTOMER_ORDER_ID desc fetch first 1 rows only",w=ware)
  foreign=q.fetchone()
  if not own or not foreign:continue
  own_order=service.get(int(own[0]),actor)
  assert own_order["ware_id"]==ware
  own_list=service.list(actor,limit=5)
  assert all(x["ware_id"]==ware for x in own_list)
  try:service.get(int(foreign[0]),actor);raise AssertionError("Foreign warehouse accepted")
  except PermissionError:pass
  results["positive_scoped_actor"]={"actor":actor,"ware":ware,"own_order":own[0],"foreign_order":foreign[0],"count":len(own_list)}
  break
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),
 round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,220)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0
 and SQL_TEXT not like '%V$SQL%' and(SQL_TEXT like '%scope_warehouse%'
 or SQL_TEXT like '%ORDER_QTY_EXACT%') order by LAST_ACTIVE_TIME desc fetch first 8 rows only""")
 results["sql"]=[list(x) for x in q.fetchall()]
Path("tmp/read1041_customer_order_scope.json").write_text(json.dumps(results,indent=2,default=str),encoding="utf-8")
print("PASS1041 current/historical/read-only/orderexact/adminbounds/missing/denied/legacy; positive scoped actor="+str("positive_scoped_actor" in results))
