exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
reader=OrderDelivery(OracleGateway())
ids=[2030]+[json.loads(Path("tmp/context303_"+str(number)+".json").read_text(encoding="utf-8"))["order_id"]for number in[291,292]]
for order in ids:reader.get(order)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def stats():
  q.execute("""select nvl(sum(EXECUTIONS),0),nvl(sum(ELAPSED_TIME),0),nvl(sum(BUFFER_GETS),0)from V$SQL
  where PARSING_SCHEMA_NAME='RABAEV'and SQL_TEXT like 'with requested%'and SQL_TEXT not like '%V$SQL%'
  and dbms_lob.instr(SQL_FULLTEXT,'leading(lineage receipt line transit loss confirmed recovered recovery_op found issue)')>0""")
  return q.fetchone()
 before=stats()
 for order in ids:
  result=reader.get(order);assert result["quantities"][0]["accepted"]=="3"
 after=stats();delta=[b-a for a,b in zip(before,after)]
 assert delta[0]==3,delta
 result=dict(executions=int(delta[0]),total_ms=float(delta[1]/1000),mean_ms=float(delta[1]/1000/delta[0]),buffers=int(delta[2]))
 Path("tmp/warm303.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))
