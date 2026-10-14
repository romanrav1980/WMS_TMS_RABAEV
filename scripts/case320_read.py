exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.interwarehouse_queue import InterwarehouseQueue
from app.modules.inventory.infrastructure.interwarehouse_incoming import InterwarehouseIncoming
ctx=json.loads(Path("tmp/context314_received.json").read_text(encoding="utf-8"));source=ctx["source"]
rows=InterwarehouseQueue(OracleGateway()).read(source["target_warehouse"],"admin",True)
row=next(r for r in rows if r["operation_id"]==source["plan_operation_id"])
assert row["pallet_identifier"]==source["physical_root"] and row["stock_pallet_identifier"]==source["lot"],row
assert row["quantity"]=="3" and row["base_uom"]=="EA",row
incoming=InterwarehouseIncoming(OracleGateway()).read(source["target_trip"],"admin")
Path("tmp/context320_read.json").write_text(json.dumps(dict(queue=row,incoming=incoming),default=str,indent=2),encoding="utf-8")
print("PASS320 physical top/commodity leaf/quantity3EA queue and current incoming SQL")
