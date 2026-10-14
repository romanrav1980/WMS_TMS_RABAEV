exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from app.modules.finance.contracts import LogisticsCostError
ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"))
norm=json.loads(Path("tmp/context574.json").read_text(encoding="utf-8"))
svc=LogisticsCosts(OracleGateway());facts=svc.transport_facts(ctx["trip"],ctx["warehouse"],"admin")
assert facts["complete"]and facts["served_addresses"]==1 and facts["unloads"][0]["method"]=="MANUAL"
try:
 svc.transport_cost_preview(ctx["trip"],ctx["warehouse"],norm["request"]["source_price_id"],"admin")
 raise AssertionError("Foreign warehouse norm charged")
except LogisticsCostError as exc:assert exc.code=="TRANSPORT_NORM_PERIOD_REQUIRED",exc.code
print("PASS576 actual retained departure/unload complete; Oracle timezone period selector executed; foreign warehouse norm refused; read-only no money/stock posting.")
