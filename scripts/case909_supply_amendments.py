"""Use saved source908 only; amend metadata, never repeat pallet birth."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.modules.integrations.application.ingestion import IdocConflict
from app.modules.integrations.domain.supply_order import read_supply_order
from app.oracle_gateway import OracleGateway
import xml.etree.ElementTree as ET
ctx=json.loads(Path("tmp/context908.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RAW_XML from RRL_SAP_SUPPLY_MESSAGE where ORDER_ID=:o order by RECEIVED_AT",o=ctx["order_id"])
 raw=q.fetchone()[0].read()
root=ET.fromstring(raw)
root.set("version","1")
try:read_supply_order(ET.tostring(root))
except ValueError as e:assert "one line per material"in str(e)
else:raise AssertionError("V1 must retain duplicate-material rejection")
root.set("version","2")
def revision(n):
 root.find("Revision").text=str(n);root.find("MessageId").text="SAP909.REVISION:"+ctx["tag"]+":"+str(n)
service=SupplyOrders(OracleGateway())
revision(2)
root.find("Lines")[1].find("Quantity").text="4"
result=service.receive(ET.tostring(root),"admin")
detail=service.get(ctx["order_id"],"admin")
assert [(x["accepted_qty"],x["remaining_qty"])for x in detail["lines"]]==[("3","0"),("0","4")],detail["lines"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COUNT1 from RRL_PRIHOD_NAKLAD_ROWS where ORDID=:d and ARTICUL=:a",d=ctx["document_id"],a=ctx["article"]);assert q.fetchall()==[(7,)]
revision(3);root.find("Lines")[0].find("Quantity").text="2"
try:service.receive(ET.tostring(root),"admin")
except IdocConflict as e:assert "less than already received"in str(e)
else:raise AssertionError("Cannot shrink accepted ERP line")
root.find("Lines")[0].find("Quantity").text="3"
root.find("Lines").remove(root.find("Lines")[1])
result=service.receive(ET.tostring(root),"admin")
detail=service.get(ctx["order_id"],"admin")
assert len(detail["lines"])==1 and detail["lines"][0]["accepted_qty"]=="3"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COUNT1 from RRL_PRIHOD_NAKLAD_ROWS where ORDID=:d and ARTICUL=:a",d=ctx["document_id"],a=ctx["article"]);assert q.fetchall()==[(3,)]
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()==(0,0)
ctx["amendments909"]={"revision":3,"v1_duplicates_rejected":True,"own_accepted_line_shrink_rejected":True,"unreceived_line_deleted_shared_row_retained":True,"canonical_planned_qty":"3","stock":[0,0]}
Path("tmp/context908.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("909 PASS revision2 source3+4/canonical7; shrink received3 to2 rejected atomically; revision3 delete unreceived shared line/canonical row3 retained; v1 duplicates rejected; own P/H0")
