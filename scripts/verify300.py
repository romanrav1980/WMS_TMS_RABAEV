exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.interwarehouse_shortage import read_shortage
for number in[291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
 x=read_shortage(OracleGateway(),ctx["receipt_operation"],"admin")
 assert x["recovered_quantity"]=="2"and x["net_unrecovered_short_quantity"]=="0"and not x["currently_missing_units"]and not x["current_unit_state_conflicts"],x
 assert x["status"]=="RECOVERED_PENDING_PLACEMENT"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for number in[291,292]:
  ctx=json.loads(Path("tmp/context300_"+str(number)+".json").read_text(encoding="utf-8"));q.execute("select BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE from RRL_CELLS where CELL=:cell_code",cell_code=ctx["receipt_result"]["cell"]);assert q.fetchone()==(1,1)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT not like '%OPT_DYN_SAMP%'and SQL_TEXT not like '%USER_TABLES%'
 and dbms_lob.instr(SQL_FULLTEXT,'RRL_INTERWARE_RECOVERY_UNIT')>0 order by ELAPSED_TIME desc fetch first 5 rows only""");rows=q.fetchall();Path("tmp/slow300.json").write_text(json.dumps(rows,indent=2),encoding="utf-8");print(json.dumps(rows))
print("PASS300 recovered2/remaining0/history retained/currentunitstate coherent/receivingcell unavailable forallocation")
