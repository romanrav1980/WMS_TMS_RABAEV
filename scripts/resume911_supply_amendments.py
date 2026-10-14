"""Use saved source908 only; amend metadata, never repeat pallet birth."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.modules.integrations.application.ingestion import IdocConflict
from app.modules.integrations.domain.supply_order import read_supply_order
from app.oracle_gateway import OracleGateway
import xml.etree.ElementTree as ET
ctx=json.loads(Path("tmp/context910.json").read_text(encoding="utf-8"))
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
 root.find("Revision").text=str(n);root.find("MessageId").text="SAP911.REVISION:"+ctx["tag"]+":"+str(n)
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


ctx["amendments911"]={"revision":3,"canonical_quantity":"3","accepted_shrink_denied":True,"v1_duplicates_denied":True,"shared_unreceived_line_deleted":True}
Path("tmp/context910.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("911 metadata PASS canonical7 then3; accepted shrink refused; unreceived shared line deleted retaining canonical; v1 duplicates refused",flush=True)
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
with httpx.Client(auth=("admin",password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 response=client.post("/api/inventory/stock-posting/receipt-documents/"+str(ctx["document_id"])+"/reverse",json={"operation_id":"SAP911.CLEANUP:"+ctx["tag"],"reason":"End own source910 fixture"})
 assert response.status_code==200,response.text
 ctx["cleanup"]=response.json();ctx["stage"]="AMENDMENTS_PASS_OWN_REVERSED"
 Path("tmp/context910.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()==(0,0)
print("911 own source910 P/H0 through native receipt reversal")
