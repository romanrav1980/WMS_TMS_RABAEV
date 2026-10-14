exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse_shortage import read_shortage
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
gw=OracleGateway()
for number in [291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
 x=read_shortage(gw,ctx["receipt_result"]["operation_id"],"admin");assert x["status"]=="RECOVERY_FINAL_RECEIPT_RECORDED"and x["net_unrecovered_short_quantity"]=="0"
 final=json.loads(Path("tmp/context303_"+str(number)+".json").read_text(encoding="utf-8"));assert OrderDelivery(gw).get(final["order_id"])["quantities"][0]["accepted"]=="3"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT not like '%OPT_DYN_SAMP%'
 and SQL_TEXT like 'with requested%'and dbms_lob.instr(SQL_FULLTEXT,'RRL_IW_RECOVERY_DISPATCH')>0
 order by ELAPSED_TIME desc fetch first 3 rows only""");result=q.fetchall();print(json.dumps(result));Path("tmp/slow303.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT like 'SELECT %'
 and(dbms_lob.instr(SQL_FULLTEXT,'RRL_IW_RECOVERY_ST_BIND')>0 or dbms_lob.instr(SQL_FULLTEXT,'RRL_IW_RECOVERY_DISPATCH')>0)
 order by ELAPSED_TIME desc fetch first 3 rows only""");print(json.dumps(q.fetchall()))
print("PASS303 current scoped shortage/history/final1+2 read")
