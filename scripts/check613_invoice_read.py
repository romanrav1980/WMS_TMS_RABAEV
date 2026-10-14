exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
d=LogisticsCosts(OracleGateway()).invoice_transport_costs(987654321,"admin")
assert d["items"]==[]and d["sources"]==[]and d["currency_totals"]==[]
print("PASS613 empty scoped invoice source/recognition/current-total branches execute without writes or invented amounts.")
