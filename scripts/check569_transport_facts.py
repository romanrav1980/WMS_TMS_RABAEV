exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from app.modules.finance.contracts import LogisticsCostError
ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"));assert ctx["done"]
finance=LogisticsCosts(OracleGateway());facts=finance.transport_facts(ctx["trip"],ctx["warehouse"],"admin")
assert not facts["complete"]and facts["load_count"]==1 and facts["destination_count"]==1
assert facts["missing"]==[{"load_operation_id":ctx["load"],"address":"Own full-pallet ST","reason":"ACTUAL_UNLOADING_REQUIRED"}],facts["missing"]
assert facts["departure"]["profile_state"]=="READY"and not facts["stock_changed"]and not facts["cost_posted"]
try:finance.transport_facts(33622,14526684,"admin");raise AssertionError("Old class inferred")
except LogisticsCostError as exc:assert exc.code=="TRANSPORT_DEPARTURE_SOURCE_REQUIRED"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_TT_VEHICLE_SOURCE S%'or upper(SQL_TEXT)like '%M.DESTINATION_ADDR%'or upper(SQL_TEXT)like '%U.METHOD%')
 order by LAST_ACTIVE_TIME desc fetch first 4 rows only""");print("SQL569",json.dumps(q.fetchall()))
print("PASS569 immutable departure1/original destination1/current scope; actual unload remains pending, old519 no fabricated profile; read-only/no money or stock effect.")
