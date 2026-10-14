exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation
from app.modules.resources.public import sync_existing_wave_tasks
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"))
print(ReplenishmentContinuation(OracleGateway(),sync_existing_wave_tasks).reconcile(ctx["ware"],"admin"))
