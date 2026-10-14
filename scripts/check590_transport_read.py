exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
d=json.loads(Path("tmp/context586.json").read_text(encoding="utf-8"));svc=LogisticsCosts(OracleGateway())
assert svc.transport_costs(d["trip"],d["warehouse"],"admin")["recognized"]==d["winner"]["result"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and upper(SQL_TEXT)like '%FROM RRL_TT_VEHICLE_SOURCE S%JOIN RRL_TRANSPORT_COST_CLAIM%'
 order by LAST_ACTIVE_TIME desc fetch first 1 rows only""");print("SQL590",json.dumps(q.fetchall()))
print("PASS590 sourcePK/claimPK/runPK read returns exact retained monetary result.")
