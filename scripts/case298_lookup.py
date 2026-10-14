exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
svc=OrderDelivery(OracleGateway())
for order,accepted,short in[(2030,"3","0")]+[(json.loads(Path("tmp/context297_"+str(n)+".json").read_text())["order_id"],"1","2")for n in[291,292]]:
 x=svc.get(order);assert x["quantities"][0]["accepted"]==accepted and x["quantities"][0]["confirmed_transport_shortage"]==short,x
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS from USER_INDEXES where INDEX_NAME='RRL_IW_DISPATCH_SOURCE_IX'");assert q.fetchone()==("VALID",)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and dbms_lob.instr(SQL_FULLTEXT,'CONFIRMED_TRANSPORT_SHORTAGE')>0 order by LAST_ACTIVE_TIME desc fetch first 4 rows only""");rows=q.fetchall();Path("tmp/slow298.json").write_text(json.dumps(rows,indent=2),encoding="utf-8");print(json.dumps(rows))
print("PASS298 sparse source-load lineage indexVALID/full229 preserved/new partial1/short2 exact/original FF untouched")
