exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.infrastructure.warehouse_depot import WarehouseDepot
from app.oracle_gateway import OracleGateway
from concurrent.futures import ThreadPoolExecutor
import uuid
service=WarehouseDepot(OracleGateway());p=Path("tmp/context285.json")
if p.exists():ctx=json.loads(p.read_text(encoding="utf-8"))
else:
 before=service.context(9807,"admin");assert not before["configured"]
 ctx={"body":{"warehouse_id":9807,"expected_version":before["version"],"depot_address":None,"reason":"Изолированная проверка конкуренции: база отправления остаётся ненастроенной"},"operations":["QA285."+uuid.uuid4().hex[:12]for _ in range(2)]}
 p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
def apply(op):
 try:return (op,200,service.apply(op,ctx["body"],"admin"))
 except Exception as e:return (op,getattr(e,"status",None),str(e))
if "winner"not in ctx:
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(apply,ctx["operations"]))
 assert sorted(r[1]for r in results)==[200,409],results
 winner=next(r for r in results if r[1]==200);ctx["winner"]=winner[0];ctx["result"]=winner[2];p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
assert service.apply(ctx["winner"],ctx["body"],"admin")==ctx["result"]
assert service.resolve(ctx["winner"],ctx["body"],"admin")["state"]=="RECORDED"
changed={**ctx["body"],"reason":"Изменённое содержимое под прежним идентификатором"}
try:service.apply(ctx["winner"],changed,"admin")
except Exception as e:assert getattr(e,"status",None)==409
else:raise AssertionError("Payload collision accepted")
assert not service.context(9807,"admin")["configured"]
print("PASS285 actual concurrent sameversion200/409, one immutable null-setting, replay/resolve recorded/bodycollision409; no guessed NICORA hub or stock writes")
