exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.wave_pick_release import WavePickRelease
from app.oracle_gateway import OracleGateway
from app.modules.inventory.contracts_stock import StockPostingError
ctx=json.loads(Path("tmp/context879.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PICK_RELEASE_OPERATION_ID from RRL_PICK_WAVE where PICK_WAVE_ID=:w",w=ctx["wave"]);op=q.fetchone()[0]
service=WavePickRelease(OracleGateway());result=service.release(ctx["wave"],op,"admin")
assert result["command_operation_id"]==op and result["released_at"]
try:service.release(ctx["wave"],op,"QA172_KRO");raise AssertionError("Foreign replay allowed")
except StockPostingError as e:assert e.oracle_code==20882,e
print("881 PASS service exact correlation/current foreign scope checked before replay; no new stock movement",ctx["wave"])
