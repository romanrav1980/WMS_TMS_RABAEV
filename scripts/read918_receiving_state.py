exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.oracle_gateway import OracleGateway
import httpx
ctx=json.loads(Path("tmp/context908.json").read_text(encoding="utf-8"))
result=SupplyOrders(OracleGateway()).get(ctx["order_id"],"admin")
assert result["receipt_state"]=="REVERSED"and result["receipt_allowed"]is False and result["gateway_contract_version"]==2
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
response=httpx.get("http://127.0.0.1:8088/api/integrations/sap/supply-orders/"+ctx["order_id"],auth=("admin",password),timeout=15)
assert response.status_code==200,response.status_code
data=response.json()
print("918 native state",result["receipt_state"],"allowed",result["receipt_allowed"],"format",result["gateway_contract_version"])
print("918 HTTP keys",data.get("receipt_state"),data.get("receipt_allowed"),data.get("gateway_contract_version"))
