exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.wave_execution_reader import execution_snapshot
from app.oracle_gateway import OracleGateway
data=execution_snapshot(OracleGateway(),403,"admin")
print(json.dumps(data,ensure_ascii=True)[:9000])
