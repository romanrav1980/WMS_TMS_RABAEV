exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.domain.delivery_windows import estimate_windows
from app.modules.transport.infrastructure.delivery_window_preview import delivery_window_preview
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
import copy,httpx
source={"operations":[{"code":"DRIVE","plan_start":"2026-11-03 08:00:00"}],
 "members":[{"address":"A","st_number":"OWN","delivery_window_from":"2026-11-03 09:00:00","delivery_window_to":"2026-11-03 10:00:00"}],
 "destination_rules":[{"address":"A","address_count":1,"unload_norm_min":30,"window_strict":1}]}
road={"stops":["A"],"source_issues":[],"legs":[{"duration_min":"20.02","unknown_reason":None},{"duration_min":"40.01","unknown_reason":None}]}
fit=estimate_windows(source,road,"Asia/Tbilisi")
assert fit["status"]=="NO_EARLIEST_WINDOW_VIOLATION"and fit["stops"][0]["service_finish_at"]=="2026-11-03T09:30:00+04:00"
assert fit["return_at"]=="2026-11-03T10:10:00.600000+04:00"
late=copy.deepcopy(source);late["members"][0]["delivery_window_to"]="2026-11-03 09:15:00"
assert estimate_windows(late,road,"Asia/Tbilisi")["stops"][0]["late_min"]=="15.0"
missing=copy.deepcopy(source);missing["members"][0]["delivery_window_from"]=None
assert estimate_windows(missing,road,"Asia/Tbilisi")["status"]=="INSUFFICIENT_EVIDENCE"
unknown=delivery_window_preview(OracleGateway(),33564,"",24,"Asia/Tbilisi","admin")
assert unknown["status"]=="INSUFFICIENT_EVIDENCE"and unknown["return_at"]is None and not unknown["operational_admission"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def context():
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TT_ROUTE_API.context",[33564,"admin",out]);return read_oracle_json(out.getvalue())
 before=context();assert before["source"]["source_contract_version"]==5
 assert all("delivery_window_from"in m for m in before["source"]["members"]);member=before["source"]["members"][0]["id"];c.rollback()
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:
  q.execute("update RRL_SBORKA_PALLETS set ZONE_TIME_PLAN_IN=timestamp '2026-11-03 09:00:00',ZONE_TIME_PLAN_OUT=timestamp '2026-11-03 10:00:00'where ID=:pallet_id",pallet_id=member)
  assert context()["source_hash"]!=before["source_hash"]
 finally:c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
 assert context()["source_hash"]==before["source_hash"];c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'
 and(dbms_lob.instr(SQL_FULLTEXT,'ADDRESS_COUNT')>0 or dbms_lob.instr(SQL_FULLTEXT,'ROAD_LEGS_PK281')>0)
 order by last_active_time desc fetch first 4 rows only""");print("SQL287_MS",q.fetchall())
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/transport/preflight/trips/33564/delivery-windows",params={"time_zone":"Asia/Tbilisi"})
 assert r.status_code==200 and r.json()["status"]=="INSUFFICIENT_EVIDENCE",r.text
print("PASS287 windowwait/unload/late/missing, sourceV5 originalwindow mutationhash+outerrollbackrestore, actualHTTP/currentownunknown/noqty/P20H20; earliestestimate not driver/admission")
