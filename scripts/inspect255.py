exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"))
a=TransportPreflight(OracleGateway()).coordination(ctx["target_trip"],"admin")
assert a["read_only"]and a["consistent_snapshot"]and not a["operational_admission"]
assert a["incoming"]["expected_deliveries"]==1 and a["warehouse_placed_deliveries"]==0
assert any(x["code"]=="COORDINATION_WAREHOUSE_PLACEMENT_PENDING"for x in a["blockers"])
print("PASS255 initial existing254 incoming source expected1/place0/no ST/no time/no false admission/no writes")
