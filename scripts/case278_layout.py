exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from decimal import Decimal
g=OracleGateway();service=LegacyPreparation(g)
source=json.loads(Path("tmp/context273.json").read_text(encoding="utf-8"));order=source["store"]["customer_order_id"];article=source["article"]
plan=service.layout(order,{article:2},"admin");assert len(plan["pallets"])==2
assert [Decimal(p["lines"][0]["quantity"])for p in plan["pallets"]]==[Decimal(24)]*2
assert not plan["stock_changed"]and not plan["st_created"]and not plan["physical_capacity_verified"]
try:service.layout(order,{article:3},"admin")
except ValueError:pass
else:raise AssertionError("Three nonempty pallets out of two boxes")
try:service.layout(order,{"foreign":1},"admin")
except ValueError:pass
else:raise AssertionError("Foreign SKU")
try:service.layout(order,{},"SAP_FILE_GATEWAY")
except PermissionError:pass
else:raise AssertionError("Gateway proposal bypass")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number",st_number="SAP_"+str(order));assert q.fetchone()==(0,)
 q.execute("select ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:order_id",order_id=order);assert q.fetchone()==(48,)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and dbms_lob.instr(SQL_FULLTEXT,'SOURCE_PICKING_READINESS268')>0
 order by last_active_time desc fetch first 2 rows only""");print("SQL278_MS",q.fetchall())
print("PASS278 current source2047 exact2wholebox proposal/foreign and impossible count refused/service denied/read-only noST/noQty; no mixed physical optimiser")
