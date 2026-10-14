exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_expenses import LogisticsExpenses
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
d=json.loads(Path("tmp/context601.json").read_text(encoding="utf-8"));assert d["done"]
svc=LogisticsExpenses(OracleGateway());sources=svc.normative_cost_sources(d["warehouse"],"admin",d["cost_operation_id"])
assert len(sources)==1 and sources[0]["original_total"]=="107.25"and sources[0]["confirmed_total"]=="0"
assert svc.normative_cost_sources(d["warehouse"],"admin","DOES.NOT.EXIST")==[]
cost=LogisticsCosts(OracleGateway()).transport_costs(d["trip"],d["warehouse"],"admin")
assert cost["recognized"]["total"]=="107.25"and cost["confirmed_total"]=="0"
rows=svc.pending(d["warehouse"],"admin")
linked=[r for r in rows if r.get("cost_correction_of_op")==d["cost_operation_id"]]
assert len(linked)==2 and all(str(r["amount"])=="-107.25"for r in linked)
print("PASS607 exact scoped normative source/unknown empty, original107.25 vs adjusted0, existing expense register two signed linked proposals, no writes.")
