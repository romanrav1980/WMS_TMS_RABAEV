exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
from app.oracle_gateway import OracleGateway
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select distinct pt.CUSTOMER_ORDER_ID from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID where wt.PICK_WAVE_ID=403 fetch first 2 rows only")
 orders=q.fetchall()
 if not orders:
  q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where WARE_ID is not null order by CUSTOMER_ORDER_ID desc fetch first 1 row only");orders=q.fetchall()
 order=int(orders[0][0])
 q.execute("select ID,WARE_ID,RRL_HAS_WRIGHT(ID,'customer_fulfillment_view')from RUSERS where ID='QA172_KRO'")
 print("existing viewer rights/warehouse",q.fetchone())
result=OrderExecution(OracleGateway()).get(order,"admin")
assert result["consistent_snapshot"]is True and result["warehouse_id"]is not None
try:OrderExecution(OracleGateway()).get(order,"QA172_KRO")
except PermissionError:print("923 existing viewer without fulfillment permission refused before quantity query")
else:raise AssertionError("Unprivileged viewer admitted")
try:OrderExecution(OracleGateway()).get(order,"NONEXISTENT923")
except PermissionError:print("923 inactive/missing viewer refused")
else:raise AssertionError("Missing viewer admitted")
Path("tmp/order923.json").write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
print("923 admin readonly PASS order",order,"warehouse",result["warehouse_id"],"status",result["execution_status"],"lines",len(result["lines"]))
