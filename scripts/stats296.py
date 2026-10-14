exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.interwarehouse_incoming import InterwarehouseIncoming
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 for table in["RRL_INTERWARE_SHORTAGE_REQUEST","RRL_INTERWARE_SHORTAGE_FACT","RRL_INTERWARE_SHORTAGE_UNIT"]:
  c.cursor().callproc("DBMS_STATS.GATHER_TABLE_STATS",["RABAEV",table])
reader=InterwarehouseIncoming(OracleGateway())
for number in[291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"));x=reader.read(ctx["target_trip"],"admin")
 assert not x["incoming_ready"]and x["plans"][0]["load_status"]=="DEPARTED"and x["plans"][0]["shortage_resolved"]==1 and x["plans"][0]["receipt_complete"]==0,x
exec(Path("scripts/slow296.py").read_text(encoding="utf-8"))
print("PASS296 after departure phase falseLOADED readiness, accounted loss maintained; gathered only three additive journal statistics")
