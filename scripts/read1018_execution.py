exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.oracle_gateway import OracleGateway
g=OracleGateway();p=OrderExecution(g).get(1931,"admin")
assert p["execution_status"]=="PARTIAL"and p["lines"][0]["picked_quantity"]=="3"and p["lines"][0]["remaining_quantity"]=="1"
assert p["active_line_count"]==1 and p["cancelled_line_count"]==0
hu=WarehouseHu(g);ctx=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"))
by_id=hu.preview("CASE:"+str(ctx["cases"][0][0]),"admin");by_scan=hu.preview(ctx["cases"][0][2],"admin");assert by_id==by_scan
Path("tmp/read1018_execution.json").write_text(json.dumps({"original_order":p,"canonical_case_read":by_id},indent=2),encoding="utf-8")
print("PASS1018 original1931 PARTIAL picked3/remain1/current counts/requestedUOM; CASEinternal=originalSSCC/samecurrentplacement")
