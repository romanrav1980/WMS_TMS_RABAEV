exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.day_reconciliation import DayReconciliation
from app.oracle_gateway import OracleGateway
from datetime import date
ctx=json.loads(Path("tmp/context543.json").read_text(encoding="utf-8"))
report=DayReconciliation(OracleGateway()).report(ctx["source"]["warehouse"],date(2026,10,12),"UTC","admin")
assert report["daily_facts"]["store_unloads_started"]==1 and report["daily_facts"]["store_unloads_completed_by_start_day"]==1,report["daily_facts"]
assert report["current_backlog"]["store_unloads_open"]==0,report["current_backlog"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),
 round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,120)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%RRL_STORE_UNLOAD_START%'or upper(SQL_TEXT)like '%RRL_STORE_UNLOAD_FACT%')
 order by ELAPSED_TIME desc fetch first 6 rows only""")
 print("SQL547",json.dumps(q.fetchall()))
Path("tmp/context547.json").write_text(json.dumps({"warehouse":ctx["source"]["warehouse"],"daily":report["daily_facts"],"backlog":report["current_backlog"]},indent=2),encoding="utf-8")
print("PASS547 one start/one completion attributed to start day, no open-unload blocker after actual original receipt; consistent readonly reconciliation.")
