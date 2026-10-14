exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.modules.finance.infrastructure.day_reconciliation import DayReconciliation
from app.modules.transport.contracts_plan import TransportPlanError
from datetime import date
g=OracleGateway();d=json.loads(Path("tmp/context276.json").read_text(encoding="utf-8"));service=StDeferral(g)
h=service.history(d["st"],0,"admin");assert len(h["rows"])==1 and h["rows"][0]["operation_id"]==d["operation"]and not h["has_more"]
assert service.history(d["st"],1,"admin")["rows"]==[]
try:service.history(d["st"],0,"SAP_FILE_GATEWAY")
except TransportPlanError as e:assert e.status==403
else:raise AssertionError("Gateway history bypass")
report=DayReconciliation(g).report(9807,date(2026,11,3),"Asia/Tbilisi","admin")
assert len(report["shipping_register"]["rows"])==2 and all(r["deferral_version"]==1 and r["trip_id"]==d["target_trip"]for r in report["shipping_register"]["rows"])
assert any(x["code"]=="shipping_members_not_departed_in_page"for x in report["open_items"])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets,substr(SQL_TEXT,1,120)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(dbms_lob.instr(SQL_FULLTEXT,'SHIPPING_MEMBER_BOUNDED275')>0 or SQL_TEXT like '%RRL_ST_DEFER_DECISION where ST_NUMBER%')
 order by last_active_time desc fetch first 6 rows only""");print("SQL276_MS",json.dumps(q.fetchall(),ensure_ascii=True))
print("PASS276 current-ware bounded immutable history/pagination/service403/samecursor daily snapshot actual2 rows deferred version1; no physical departure proof")
