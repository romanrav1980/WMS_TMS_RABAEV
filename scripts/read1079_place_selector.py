exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest
from app.oracle_gateway import OracleGateway
svc=StDeferWaiting(OracleGateway())
result=svc.read("DEC987:4bb85f1f15","admin",0,20)
assert result["selection_required"]is False and len(result["available_places"])==1,result
assert result["available_places"][0]["root_identifier"]=="HU1069:4bb85f1f15"and result["available_places"][0]["available"]is True
legacy=json.loads(Path("tmp/context1072.json").read_text(encoding="utf-8"))
assert svc.plan(WaitingTaskRequest(**legacy["request"]),"admin")==legacy["result"]
Path("tmp/read1079_place_selector.json").write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
print("PASS1079 currentoneTOP selector/no requiredchoice/default legacycached compatibility")
