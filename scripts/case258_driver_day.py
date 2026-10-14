"""Cross-trip exact clipping and actual same-snapshot source proof, no new fixtures."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.domain.driver_day import planned_day_drive
from app.modules.transport.public import TransportPreflight
from app.oracle_gateway import OracleGateway
def op(key,a,b):return dict(operation_id=key,operation_code="DRIVE",plan_start_at=a,plan_end_at=b)
a=op(1,"2026-10-11T23:30:00+04:00","2026-10-12T01:30:00+04:00")
day1=planned_day_drive([a],"2026-10-10T20:00:00+00:00","2026-10-11T20:00:00+00:00")
day2=planned_day_drive([a],"2026-10-11T20:00:00+00:00","2026-10-12T20:00:00+00:00")
assert day1["drive_min"]=="30.0"and day2["drive_min"]=="90.0"
b=op(2,"2026-10-11T01:00:00+00:00","2026-10-11T06:00:00+00:00")
c=op(3,"2026-10-11T08:00:00+00:00","2026-10-11T13:00:00+00:00")
assert planned_day_drive([b,c],"2026-10-11T00:00:00+00:00","2026-10-12T00:00:00+00:00")["limit_exceeded"]
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"))
result=TransportPreflight(OracleGateway()).trip_time(ctx["target_trip"],"UTC","admin")
days=result["driver_days"];assert len(days["days"])==1
assert not days["driver_day_complete"]and not days["legal_compliance_verified"]
proof=next(x for x in days["days"][0]["sources"]if x["trip_id"]==ctx["target_trip"])
assert proof["unknown_drive_operation_ids"]and proof["source_hash"]==ctx["time256"]["source_hash"]
assert days["days"][0]["unresolved_trip_ids"],"Original sourceTT lackscurrent approvedregion and mustremainunresolved"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like 'select distinct t.ID from RRL_TRANSPORT_TASK t%o.TT_ID=t.ID%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
print("PASS258 exactmidnight/+04/UTC clipping/combinedplanned600exceeds540/sameSource254 nativeapprovedV2/zeroactualrouteunknown/sourcepeer unresolved/sameREADONLY/protected20-20/no writes")
