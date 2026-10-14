exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from concurrent.futures import ThreadPoolExecutor
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
from app.modules.platform.public import read_oracle_json
ctx_path=Path("tmp/context563.json");ctx=json.loads(ctx_path.read_text(encoding="utf-8"))
assert "result_v2"not in ctx,"Already completed; only exact replay allowed"
tag=ctx["tag"];vehicle=ctx["vehicle_id"];body=ctx["request"];service=VehicleProfiles(OracleGateway())
source=Path("scripts/case563_vehicle_profile.py").read_text(encoding="utf-8")
exec(source[source.index("def publish(request):"):])
