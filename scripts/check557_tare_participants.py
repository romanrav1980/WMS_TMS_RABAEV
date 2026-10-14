exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.tare import Tare
ctx=json.loads(Path("tmp/context553.json").read_text(encoding="utf-8"));assert ctx["done"]
service=Tare(OracleGateway(),lambda *args:None)
context=service.context(ctx["trip"],"admin")
assert context["participant"]["all_warehouses"] and context["participant"]["can_offer"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_TRANSPORT_DRIVER_USER where DRIVER_ID=:driver and USER_ID='admin'and ACTIVE=1",driver=ctx["driver"])
 assert context["participant"]["trip_driver"]==bool(q.fetchone()[0])
 q.execute("select DELETED from RUSERS where ID=:actor",actor=ctx["users"][1]["id"]);assert q.fetchone()==(1,)
warehouses=[r["id"]for r in context["warehouses"]];assert ctx["warehouse"]in warehouses
offers=service.offers(ctx["trip"],"admin")
own=[r for r in offers if r["operation_id"].startswith("TRACE553.OFFER:"+ctx["tag"])]
assert len(own)==4
assert sum(r["damage_operation_id"]=="TRACE553.DAMAGE:"+ctx["tag"]for r in own)==2
assert all(r["accept_operation_id"]for r in own)
print("PASS557 existing TarePanel backend context exposes actual current signatures, priority trip warehouse and original damage on two accepted returns. No new actors/bindings/transfers.")
