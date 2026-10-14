exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse_shortage import read_shortage
from app.oracle_gateway import OracleGateway
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for number in [291,292]:
  ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
  x=read_shortage(OracleGateway(),ctx["receipt_result"]["operation_id"],"admin")
  assert x["status"]=="RECOVERED_PLACED_PENDING_REDELIVERY"and x["net_unrecovered_short_quantity"]=="0"and x["recovery_placement_operation_id"]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT not like '%OPT_DYN_SAMP%'
 and(dbms_lob.instr(SQL_FULLTEXT,'RRL_IW_RECOVERY_PUT_PLAN')>0 or dbms_lob.instr(SQL_FULLTEXT,'RRL_IW_RECOVERY_PLACEMENT')>0)
 and SQL_TEXT not like 'CREATE %'and SQL_TEXT not like '%USER_TABLES%'
 order by ELAPSED_TIME desc fetch first 4 rows only""")
 result=q.fetchall();Path("tmp/slow301.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))
print("PASS301 scoped placement current read on same snapshot")
