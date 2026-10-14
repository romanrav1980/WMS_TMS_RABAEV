"""Changed planning diagnostic: continuity is not reset by warehouse work."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.domain.driver_rest import evaluate_driver_rest
from app.modules.transport.public import TransportPreflight
from app.oracle_gateway import OracleGateway
from datetime import datetime,timedelta,timezone
base=datetime(2026,10,15,8,tzinfo=timezone.utc)
def ops(stages):
 result=[];start=base
 for i,(code,minutes)in enumerate(stages):
  end=start+timedelta(minutes=minutes)
  result.append(dict(operation_id=i+1,operation_code=code,plan_start_at=start.isoformat(),plan_end_at=end.isoformat()))
  start=end
 return result
bad=evaluate_driver_rest(ops([("DRIVE",120),("UNLOAD",30),("DRIVE_BACK",1)]))
assert any(x["code"]=="DRIVER_CONTINUOUS_DRIVE_LIMIT"for x in bad["violations"])
good=evaluate_driver_rest(ops([("DRIVE",120),("REST",15),("DRIVE_BACK",120)]))
assert not good["violations"]and not good["unknown_intervals"]
short=evaluate_driver_rest(ops([("DRIVE",120),("REST",14),("DRIVE_BACK",1)]))
assert {x["code"]for x in short["violations"]}=={"DRIVER_BREAK_TOO_SHORT","DRIVER_CONTINUOUS_DRIVE_LIMIT"}
long=evaluate_driver_rest(ops([("DRIVE",600)]))
assert any(x["code"]=="DRIVER_TRIP_DRIVE_LIMIT"for x in long["violations"])
assert evaluate_driver_rest(ops([("DRIVE",0)]))["status"]=="INSUFFICIENT_EVIDENCE"
result=TransportPreflight(OracleGateway()).trip_time(33530,"Asia/Tbilisi","admin")
assert result["driver_rest"]["coverage"]=="SINGLE_TRIP_PLANNED_OPERATIONS"
assert not result["driver_rest"]["driver_day_complete"]and not result["operational_admission"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-11-256-material-transport-time-source'");assert q.fetchone()==("APPLIED",)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like 'select ID,OPERATION_CODE,ORD,%from_tz%' and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
print("PASS257 continuity/work/explicitbreak/shortbreak/limit/unknown/real original12/planning-only/no writes/protected20-20/ledger256applied")
