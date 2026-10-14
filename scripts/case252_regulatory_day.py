exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.day_reconciliation import DayReconciliation
from app.modules.finance.contracts import LogisticsCostError
from datetime import date
import httpx
g=OracleGateway();service=DayReconciliation(g);receiver="WR23413508027ed";ware=51365792
r=service.report(ware,date(2026,10,11),"Asia/Tbilisi",receiver)
groups=r["regulatory"]["groups"]
for kind in["MARKED_GOODS_DISPOSED","MARKED_SUPPLIER_RETURN_DISPATCHED"]:
 selected=[x for x in groups if x["event_type"]==kind]
 assert {x["system_code"]for x in selected}>={"CRPT","EGAIS"},selected
 assert all(x["source_operation_unverified_count"]==0 and x["government_acceptance"]=="NOT_VERIFIED_BY_THIS_REPORT"for x in selected)
assert r["consistent_snapshot"] and not r["day_closed"] and not r["regulatory"]["government_ack_reconciled"]
assert not r["regulatory"]["quantity_totals_inferred"] and r["regulatory"]["message_count"]>=4
assert any(x["code"]=="regulatory_ack_not_reconciled"for x in r["open_items"])
try:service.report(65691543,date(2026,10,11),"Asia/Tbilisi",receiver)
except LogisticsCostError as exc:assert exc.status==403
else:raise AssertionError("Foreign regulatory warehouse exposed")
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 h=client.get("http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/51365792",params={"business_date":"2026-10-11"})
 assert h.status_code==200,(h.status_code,h.text[:500])
 assert h.json()["regulatory"]["message_count"]==r["regulatory"]["message_count"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL
 where sql_text like 'select e.TARGET_SYSTEM,e.EVENT_TYPE,e.STATUS,count(*),%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""");print("SQL_MS",q.fetchall())
print("PASS252 existing actual marked disposal/supplier events CRPT+EGAIS samewarehouse current root APPLIED proof/source scope/read-only/foreign403/HTTP200/no quantity inference/no govACK/no dayclose/protected20-20/no new fixtures")
