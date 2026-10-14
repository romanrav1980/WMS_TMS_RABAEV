exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.services.customer_order_service import CustomerOrderService
from app.oracle_gateway import OracleGateway
service=CustomerOrderService(OracleGateway());historical=service.get_fulfillment(1931,"admin")
assert len(historical)==1 and historical[0]["status"]=="SHIPPED"and historical[0]["physical_composition"][0]["quantity"]=="3"
assert historical[0]["case_place_current"]is False
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CUSTOMER_ORDER_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1131");oid=int(q.fetchone()[0])
current=service.get_fulfillment(oid,"admin")
assert len(current)==1 and current[0]["case_identifier"]=="CP553000000001131"and current[0]["case_current_version"]==10 and current[0]["case_binding_version_matches"]is True and current[0]["case_place_current"]is True,current
try:service.get_fulfillment(oid,"QA172_KRO");raise AssertionError("Denied current actor was allowed")
except PermissionError:pass
Path("tmp/read1027_fulfillment.json").write_text(json.dumps({"historical":historical,"current_order":oid,"current":current,"denied_existing_actor":True},indent=2,default=str),encoding="utf-8")
print("PASS1027 originalSHIPPED3/currentCASE10FF10/currentcarrier+cell/scopedread/deniedQAactor/noquantitychange")
