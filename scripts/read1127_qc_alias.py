exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.modules.inventory.contracts_stock import StockPostingError
svc=OutgoingQuality(OracleGateway());r={}
canonical="CASE.QC.ST:4bb85f1f15:1131"
for value in("CP553000000001131","CASE:1131",canonical):
 snap=svc.status(value,"admin")
 assert snap["shipment_identifier"]==canonical and snap["case_content_version"]==20,snap
 if value!=canonical:assert snap["requested_identifier"]==value
 r[value]={"shipment_identifier":snap["shipment_identifier"],"case_content_version":snap["case_content_version"],"ready":snap["ready"],"requested_identifier":snap.get("requested_identifier")}
try:svc.status("CP553000000001131","nonexistent1127")
except StockPostingError as exc:assert exc.code=="OUTGOING_QC_FORBIDDEN"
else:raise AssertionError("Missing actor received QC")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and SQL_TEXT like 'select distinct PALLET_UID from (%'and executions>0 order by last_active_time desc fetch first 2 rows only");r["slow_sql"]=[list(x)for x in q]
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
Path("tmp/read1127_qc_alias.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
print(json.dumps(r,ensure_ascii=True))
