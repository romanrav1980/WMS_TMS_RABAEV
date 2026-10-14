exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.finance.infrastructure.shipping_register import report
from app.modules.finance.contracts import LogisticsCostError
from datetime import date
import httpx
g=OracleGateway();planned=report(g,9807,date(2026,11,3),0,1,"admin")
assert planned["has_more"]and len(planned["rows"])==1 and planned["rows"][0]["st_number"]=="SAP_2046"
next_page=report(g,9807,date(2026,11,3),planned["next_after_id"],1,"admin")
assert next_page["rows"][0]["st_number"]=="SAP_2046"and next_page["rows"][0]["st_pallet_id"]!=planned["rows"][0]["st_pallet_id"]
assert all(row["physical_state"]=="PHYSICAL_LOADING_NOT_CONFIRMED"for row in planned["rows"]+next_page["rows"])
assert not planned["shipping_zone_empty_confirmed"]and not planned["rows_are_physical_place_count"]
try:report(g,9807,date(2026,11,3),0,20,"SAP_FILE_GATEWAY")
except LogisticsCostError as e:assert e.status==403
else:raise AssertionError("Gateway view bypass")
# Published warehouse1 staging coverage is explicitly partial even if no positive rows.
published=report(g,1,date(2026,10,11),0,20,"admin");assert not published["all_shipping_zone_coverage_verified"]and not published["shipping_zone_empty_confirmed"]
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/finance/day-reconciliation/warehouses/9807/shipping-register",params={"business_date":"2026-11-03","limit":1})
 assert r.status_code==200,r.text
 assert r.json()["rows"][0]["st_pallet_id"]==planned["rows"][0]["st_pallet_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%with declared as(%'or SQL_TEXT like '%select p.ID,p.ST_NUMBER,p.PALLET_UID,p.CONDITION,p.TRANSTASK_ID%')
 order by last_active_time desc fetch first 4 rows only""");print("SQL_MS",json.dumps(q.fetchall(),ensure_ascii=True))
print("PASS275 existingSAP2members datedcursor/physicalnotloaded current proof/declaredstage-gate cells/coverage unknown-no falseempty/currentservice403/HTTP/P20H20/no writes")
