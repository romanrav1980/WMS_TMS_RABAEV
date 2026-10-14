exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.day_reconciliation import DayReconciliation
from datetime import date
import httpx
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));ware=ctx["source_ware"];task=ctx["task_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select STATUS,to_char(STARTED_AT_INSTANT at time zone 'Asia/Tbilisi','YYYY-MM-DD'),
 to_char(FINISHED_AT_INSTANT at time zone 'Asia/Tbilisi','YYYY-MM-DD'),FINISHED_AT_INSTANT
 from RRL_WAREHOUSE_TASK where TASK_ID=:tid""",tid=task)
 state,day,finished_day,instant=q.fetchone();assert state=="DONE"and day==finished_day and instant is not None
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","warehouse_task_edit"])
 try:
  for tid,sql in[(task,"update RRL_WAREHOUSE_TASK set FINISHED_AT_INSTANT=null where TASK_ID=:tid"),(953,"update RRL_WAREHOUSE_TASK set FINISHED_AT_INSTANT=systimestamp where TASK_ID=:tid")]:
   try:q.execute(sql,tid=tid)
   except oracledb.DatabaseError as exc:assert exc.args[0].code==20863,str(exc);c.rollback()
   else:raise AssertionError("Clock fabricated or cleared")
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
service=DayReconciliation(OracleGateway());r=service.report(ware,date.fromisoformat(day),"Asia/Tbilisi","admin")
assert r["daily_facts"]["warehouse_tasks_started"]==1 and r["daily_facts"]["warehouse_tasks_finished"]==1,r["daily_facts"]
assert r["warehouse_task_time_coverage"]["daily_counts_use_aware_instants"]and not r["warehouse_task_time_coverage"]["legacy_wall_dates_reinterpreted"]
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 h=client.get(f"http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/{ware}",params={"business_date":day})
 assert h.status_code==200,(h.status_code,h.text[:500])
 assert h.json()["daily_facts"]["warehouse_tasks_finished"]==1
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL
 where sql_text like 'select count(*)from RRL_WAREHOUSE_TASK where(FROM_WARE_ID=%'
 and executions>0 order by last_active_time desc fetch first 4 rows only""");print("SQL_MS",q.fetchall())
print("PASS254 actual979 native explicit start/TASK_COMPLETE3/late root rollback clock+qty/replay stable then originalQC6/load/depart/3sameunits6codes; aware daystart1finish1/oldDONE notbackfilled/clock immutable/HTTP200/protected20-20")
