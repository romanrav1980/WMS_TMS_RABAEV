exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.wave_pick_release import WavePickRelease
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"))
result=WavePickRelease(OracleGateway()).preview(ctx["wave"],"admin")
print(json.dumps(result,ensure_ascii=True,default=str));Path("tmp/read957.json").write_text(json.dumps(result,default=str),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_WAVE_PICK_CMD'and TYPE='PACKAGE BODY'order by LINE")
 Path("tmp/957_wave_pick.sql").write_text("".join(r[0]for r in q),encoding="utf-8")
 q.execute("select CASE_PICK_TASK_ID,STATUS,TOTAL_LINES from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w",w=ctx["wave"]);print("CASES",q.fetchall())
