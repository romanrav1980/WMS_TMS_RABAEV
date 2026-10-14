exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.preparation_readiness import preparation_readiness
r=preparation_readiness(OracleGateway(),2047,"admin")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select ARTICUL,SEQ,SEQ_GROUP from RRL_COMPL_SEQ where WARE_ID=:w and ARTICUL in(select ARTICUL from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:o)order by ARTICUL,SEQ,SEQ_GROUP",w=r["warehouse_id"],o=2047)
 r["sequence"]=[list(x)for x in q]
Path("tmp/read1112_auto_source.json").write_text(json.dumps(r,indent=2,default=str),encoding="utf-8")
print(json.dumps(r,ensure_ascii=True,default=str))
