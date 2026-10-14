exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.infrastructure.operation_plan import generate_existing_operations
from app.oracle_gateway import OracleGateway
p=Path("tmp/repair288_own_chain.json")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ST_NUMBER from RRL_SBORKA_PALLETS where TRANSTASK_ID=33564 order by ID")
 assert q.fetchall()==[("M270:4edcbf41c6",),("M270:4edcbf41c6",)]
 q.execute("select count(*)from RRL_TT_HU_LOAD_FACT where TT_ID=33564 and STATUS in('LOADED','DEPARTED')");assert q.fetchone()==(0,)
 q.execute("select ID,OPERATION_CODE,PLAN_START,PLAN_END,FACT_START,FACT_END from RRL_TT_OPERATIONS where TT_ID=33564 order by ID")
 before=q.fetchall();assert len(before)==12 and all(r[4]is None and r[5]is None for r in before)
 if not p.exists():p.write_text(json.dumps({"trip_id":33564,"before":[list(r)for r in before]},default=str,indent=2),encoding="utf-8")
 c.rollback()
rows=generate_existing_operations(OracleGateway(),33564,"admin");assert len(rows)==12
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,OPERATION_CODE,PLAN_START,PLAN_END,FACT_START,FACT_END from RRL_TT_OPERATIONS where TT_ID=33564 order by ID")
 after=q.fetchall();assert [r[0]for r in before]==[r[0]for r in after]and all(r[4]is None and r[5]is None for r in after)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("REPAIR288 existingown33564 planned ARM regenerated through original owner/same12IDs/no facts orstock; timeapprovals/history notautorenewed")
