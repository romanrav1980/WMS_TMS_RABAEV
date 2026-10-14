from decimal import Decimal
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
from app.oracle_gateway import OracleGateway
output={}
for n in (172,173):
 fixture=json.loads(Path("tmp/ni033_mixed"+str(n)+"_fixture.json").read_text(encoding="utf-8"))
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select CUSTOMER_ORDER_ID,STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:f",f=fixture["ff"]);order,status,qty=q.fetchone()
 result=OrderExecution(OracleGateway()).get(int(order),"admin")
 assert status=="SHIPPED"and str(qty)=="3"
 assert sum(Decimal(x["picked_quantity"])for x in result["lines"])==3,result
 output[str(n)]={"fulfillment_status":status,"physical_shipped":"3","execution":result}
 print("929 source",n,"order",order,"execution",result["execution_status"],[(x["picked_quantity"],x["remaining_quantity"])for x in result["lines"]])
Path("tmp/order929.json").write_text(json.dumps(output,indent=2,default=str),encoding="utf-8")
