exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from app.modules.finance.contracts import LogisticsCostError
import httpx
ctx=json.loads(Path("tmp/context519.json").read_text(encoding="utf-8"));trip=ctx["trip"];ware=ctx["warehouse"]
svc=LogisticsCosts(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PRICE,PAY_REGION,ADDR_PREMIO from RRL_TRANSPORT_TASK where ID=:trip",trip=trip);before=q.fetchone()
 q.execute("select count(*)from RRL_EVENTS");events=q.fetchone()[0]
 r=svc.transport_tariff_sources(trip,ware,"admin")
 assert r["selection_state"]=="TARIFF_SOURCE_MISSING"and r["candidates"]==[],r
 assert r["tariff_selected"]is False and r["price_changed"]is False and r["missing_contract_fields"],r
 try:svc.transport_tariff_sources(trip,9807,"admin")
 except LogisticsCostError as e:assert e.code=="COST_TRIP_WAREHOUSE_SOURCE_REQUIRED"
 else:raise AssertionError("Foreign source warehouse accepted")
 q.execute("select PRICE,PAY_REGION,ADDR_PREMIO from RRL_TRANSPORT_TASK where ID=:trip",trip=trip);assert q.fetchone()==before
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==events
 Path("tmp/context527.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print("PASS527 real retained trip source missing tariff explicit; no arbitrary fee/currency/method assumed; current source WARE required; PRICE/PAY_REGION/ADDR_PREMIO/goods unchanged.")
