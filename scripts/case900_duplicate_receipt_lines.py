"""Own new SAP source/lot only; prove per-line progress through original root receipt."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
import xml.etree.ElementTree as ET
import httpx
from app.modules.integrations.infrastructure.supply_orders import SupplyOrders
from app.modules.integrations.infrastructure.supply_reads import pallet_plan
from app.oracle_gateway import OracleGateway
path=Path("tmp/context900.json")
assert not path.exists(),"One-shot factory: use saved context for reads/replay, never recreate"
source=json.loads(Path("tmp/context669.json").read_text(encoding="utf-8"))
tag=uuid4().hex
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select DEFAULT_RECEIVE_CELL from RRL_WARES where ID=:w",w=source["warehouse"]);receive=q.fetchone()[0]
 q.execute("select ID,PASS from RUSERS where ID='admin' and nvl(DELETED,0)=0");actor,password=q.fetchone()
 protected=json.loads(Path("tmp/context688.json").read_text(encoding="utf-8"))
 q.execute("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid order by CELL",p_uid=protected["uid"]);protected_before=q.fetchall()
ctx=dict(tag=tag,warehouse=source["warehouse"],article=source["article"],uid="LEGACY.SAP.900:"+tag,stage="NEW")
units=[dict(unit_id=str(i),quantity="1",codes=[
 dict(system_code="CRPT",profile_code="TOBACCO",code=source["barcode"]+tag[:5]+str(i).zfill(2)),
 dict(system_code="EGAIS",profile_code="ALCOHOL",code=("QA900"+tag+str(i)).ljust(68,"X"))])for i in range(1,4)]
aggregate=dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B900:"+tag)
body=dict(operation_id="SAP900.BIRTH:"+tag,line_number="1",pallet_identifier=ctx["uid"],quantity="3",
 supplier_batch="PB900:"+tag,expiry_date="2030-01-01",gross_weight="3",
 units=[dict(unit_id=u["unit_id"],quantity=u["quantity"],codes=[u["codes"][0]])for u in units],aggregations=[aggregate])
ctx["body"]=body
def save():path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
save()
root=ET.Element("WarehouseSupplyOrder",version="1")
def fields(node,values):
 for key,value in values.items():ET.SubElement(node,key).text=str(value)
fields(root,dict(Sender="OWN.QA.SAP",MessageId="SAP900.SUPPLY:"+tag,OrderNumber="SAP900:"+tag[:10],
 Revision=1,WarehouseId=ctx["warehouse"],ReceiveCell=receive,Supplier="Private duplicate-line900"))
lines=ET.SubElement(root,"Lines")
for number in ("1","2"):
 line=ET.SubElement(lines,"Line");fields(line,dict(LineNumber=number,Material=ctx["article"]))
 ET.SubElement(line,"Quantity",unit="EA").text="3"
container=ET.SubElement(ET.SubElement(root,"Aggregations"),"Aggregation")
fields(container,dict(LineNumber="1",System="EGAIS",Profile="ALCOHOL",Level="BOX",Code=aggregate["code"]))
members=ET.SubElement(container,"Units")
for unit in units:fields(ET.SubElement(members,"Unit"),dict(UnitId=unit["unit_id"],Quantity="1",Code=unit["codes"][1]["code"]))
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 try:
  response=client.post("/api/integrations/sap/supply-orders",content=ET.tostring(root,encoding="utf-8"),headers={"Content-Type":"application/xml"})
  assert response.status_code==202,response.text
  ctx.update(order_id=response.json()["order_id"],document_id=response.json()["incoming_document_id"],stage="IMPORTED");save()
  response=client.post("/api/receiving/supply-orders/"+ctx["order_id"]+"/pallets",json=body)
  assert response.status_code==201,response.text
  receipt=response.json();ctx.update(receipt=receipt,stage="RECEIVED");save()
  assert receipt["marking_units"]==3 and receipt["sscc"]is None
  assert client.post("/api/receiving/supply-orders/"+ctx["order_id"]+"/pallets",json=body).json()==receipt
  service=SupplyOrders(OracleGateway());detail=service.get(ctx["order_id"],actor)
  by_line={line["line_number"]:line for line in detail["lines"]}
  assert by_line["1"]["accepted_qty"]=="3"and by_line["1"]["remaining_qty"]=="0",by_line
  assert by_line["2"]["accepted_qty"]=="0"and by_line["2"]["remaining_qty"]=="3",by_line
  proposal=pallet_plan(OracleGateway(),ctx["order_id"],{"line_number":"2","pallet_count":1},actor)
  assert proposal["quantities"]==["3"]and proposal["read_only"],proposal
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();q.execute("select nvl(sum(UNIT_COUNT),0)from RRL_PALLETS where PRIHOD_NAKLAD_ID=:d and ARTICUL=:a",d=ctx["document_id"],a=ctx["article"])
   assert q.fetchone()==(3,),"Old document/SKU query should wrongly give both lines3"
  ctx.update(stage="PER_LINE_PASS",line1_accepted="3",line2_accepted="0",line2_remaining="3",proposal=proposal);save()
  print("900 PASS same SKU two lines3/3; real marked root receipt3/6codes only line1; line1 accepted3/line2 accepted0 and remaining3; exact replay; original layout proposes3",flush=True)
 finally:
  if "receipt"in ctx:
   reverse_body={"operation_id":"SAP900.CLEANUP:"+tag,"reason":"End own duplicate-line receiving fixture"}
   response=client.post("/api/inventory/stock-posting/receipt-documents/"+str(ctx["document_id"])+"/reverse",json=reverse_body)
   assert response.status_code==200,("Own cleanup refused",response.status_code,response.text)
   ctx["cleanup"]=response.json();ctx["stage"]="PER_LINE_PASS_OWN_REVERSED";save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()==(0,0)
 q.execute("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid order by CELL",p_uid=protected["uid"]);assert q.fetchall()==protected_before
 print("900 own new P/H0 through receipt reversal; protected688 stock/version unchanged")
