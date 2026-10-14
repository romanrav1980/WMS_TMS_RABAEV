exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.public import StockCommand,StockPosting
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"))
assert ctx["stage"]=="WAVE_LAUNCH_STARTED"
op=ctx["launch"]["body"]["detail"]["operation_id"]
result=StockPosting().post(StockCommand(operation_id=op,command_type="WAVE_LAUNCH",actor="admin",lines=(),source={"wave_id":ctx["wave_id"]},metadata={}))
ctx["launch_native"]=result;Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print(json.dumps(result,default=str))
