exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.return_receiving_reads import page,source,policy
from app.modules.inventory.contracts_store_returns import StoreReturnReceiveError
from app.oracle_gateway import OracleGateway
g=OracleGateway()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select s.WARE_ID,count(*)from RRL_STORE_RETURN_PICKUP p join RRL_STORE_RETURN_HANDOVER h on h.OPERATION_ID=p.HANDOVER_OPERATION_ID
 join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID join RRL_STORE_RETURN_SAP s on s.OPERATION_ID=t.SAP_OPERATION_ID
 where not exists(select 1 from RRL_STORE_RETURN_RECEIPT r where r.PICKUP_OPERATION_ID=p.OPERATION_ID)
 group by s.WARE_ID order by count(*)desc fetch first 3 rows only""");candidates=q.fetchall()
print("PENDING_COUNTS",candidates)
ware=candidates[0][0]if candidates else 13583852
p=page(g,ware,"admin",limit=1);assert p["consistent_snapshot"]and not p["stock_changed"]
for row in p["items"]:assert row["marked_unit_control"]is None and not row["full_source_loaded"]
if p["items"]:
 item=source(g,ware,p["items"][0]["pickup_operation_id"],"admin");assert item["full_source_loaded"]and item["consistent_snapshot"]
 if p["has_more"]:
  following=page(g,ware,"admin",after=p["next_after"],limit=1);assert following["items"]and following["items"][0]["pickup_operation_id"]!=p["items"][0]["pickup_operation_id"]
Path("tmp/context283.json").write_text(json.dumps({"ware":ware,"page":p},default=str),encoding="utf-8")
for read in [lambda:page(g,ware,"SAP_FILE_GATEWAY"),lambda:policy(g,ware,"SAP_FILE_GATEWAY")]:
 try:read()
 except StoreReturnReceiveError as e:assert e.status==403
 else:raise AssertionError("Gateway return rights bypass")
try:source(g,ware,"MISSING.QA283","admin")
except StoreReturnReceiveError as e:assert e.status==404
else:raise AssertionError("Nonpending source shown")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and dbms_lob.instr(SQL_FULLTEXT,'RETURN_RECEIVING_BOUNDED283')>0
 order by last_active_time desc fetch first 3 rows only""");print("SQL283_MS",q.fetchall())
print("PASS283 currentWARE/right oneRO empty pagedqueue/gateway403/nonpending404/no writes; actual pending positive/detail/cursor continuation remains independent")
