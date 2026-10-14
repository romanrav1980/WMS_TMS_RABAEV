"""Only own new pallet in retained private SKU/WARE; durable stage recovery."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
import xml.etree.ElementTree as ET
import httpx
path=Path("tmp/context688.json")
source=json.loads(Path("tmp/context669.json").read_text())
if path.exists():ctx=json.loads(path.read_text())
else:
 tag=uuid4().hex
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select DEFAULT_RECEIVE_CELL from RRL_WARES where ID=:ware",ware=source["warehouse"]);receive=q.fetchone()[0]
 ctx=dict(tag=tag,warehouse=source["warehouse"],article=source["article"],gtin=source["barcode"],uid="LEGACY.SAP.688:"+tag,receive=receive,stage="NEW")
 ctx["units"]=[dict(unit_id=str(i),quantity="1",codes=[dict(system_code="CRPT",profile_code="TOBACCO",code=ctx["gtin"]+tag[:5]+str(i).zfill(2)),dict(system_code="EGAIS",profile_code="ALCOHOL",code=("QA688"+tag+str(i)).ljust(68,"X"))])for i in range(1,4)]
 ctx["aggregation"]=dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B688:"+tag)
 ctx["body"]=dict(operation_id="SAP688.BIRTH:"+tag,line_number="1",pallet_identifier=ctx["uid"],quantity="3",supplier_batch="PB688:"+tag,expiry_date="2030-01-01",gross_weight="3",units=[dict(unit_id=u["unit_id"],quantity=u["quantity"],codes=[u["codes"][0]])for u in ctx["units"]],aggregations=[ctx["aggregation"]])
 path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
def save():path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'and nvl(DELETED,0)=0");user,password=q.fetchone()
with httpx.Client(auth=(user,password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 if "order_id"not in ctx:
  root=ET.Element("WarehouseSupplyOrder",version="1")
  def fields(node,values):
   for key,value in values.items():ET.SubElement(node,key).text=str(value)
  fields(root,dict(Sender="OWN.QA.SAP",MessageId="SAP688.SUPPLY:"+ctx["tag"],OrderNumber="SAP688:"+ctx["tag"][:10],Revision=1,WarehouseId=ctx["warehouse"],ReceiveCell=ctx["receive"],Supplier="Private688"))
  line=ET.SubElement(ET.SubElement(root,"Lines"),"Line");fields(line,dict(LineNumber="1",Material=ctx["article"]));ET.SubElement(line,"Quantity",unit="EA").text="3"
  container=ET.SubElement(ET.SubElement(root,"Aggregations"),"Aggregation")
  fields(container,dict(LineNumber="1",System="EGAIS",Profile="ALCOHOL",Level="BOX",Code=ctx["aggregation"]["code"]))
  units=ET.SubElement(container,"Units")
  for unit in ctx["units"]:fields(ET.SubElement(units,"Unit"),dict(UnitId=unit["unit_id"],Quantity="1",Code=unit["codes"][1]["code"]))
  response=client.post("/api/integrations/sap/supply-orders",content=ET.tostring(root,encoding="utf-8"),headers={"Content-Type":"application/xml"});assert response.status_code==202,response.text
  ctx["order_id"]=response.json()["order_id"];ctx["stage"]="SUPPLY_IMPORTED";save()
 if "receipt"not in ctx:
  response=client.post("/api/receiving/supply-orders/"+ctx["order_id"]+"/pallets",json=ctx["body"]);assert response.status_code==201,response.text
  ctx["receipt"]=response.json();ctx["stage"]="RECEIVED";save()
 receipt=ctx["receipt"];assert receipt["pallet_identifier"]==ctx["uid"]and receipt["sscc"]is None and receipt["marking_units"]==3
 response=client.post("/api/receiving/supply-orders/"+ctx["order_id"]+"/pallets",json=ctx["body"]);assert response.status_code==201 and response.json()==receipt
 if "putaway"not in ctx:
  response=client.post("/api/receiving/putaway/"+str(receipt["task_id"])+"/complete",json=dict(scanned_pallet=ctx["uid"],scanned_from_cell=ctx["receive"],scanned_to_cell=receipt["putaway_cell"]));assert response.status_code==200,response.text
  ctx["putaway"]=response.json();ctx["stage"]="PUTAWAY_DONE";save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SSCC from RRL_PALLETS where UID_PALLET=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()[0]is None
 q.execute("select SSCC,STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:task",task=receipt["task_id"]);assert q.fetchone()==(None,"DONE")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["uid"],cell=receipt["putaway_cell"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=ctx["uid"]);assert q.fetchone()[0]==3
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_CRPT_AGGREGATION where UID_PALLET=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_CRPT_CODES where UID_PALLET=:p_uid and PARENT_SSCC is not null",p_uid=ctx["uid"]);assert q.fetchone()[0]==0
ctx["stage"]="DONE";save()
print(json.dumps({"status":"PASS","internal_uid_length":len(ctx["uid"]),"P":3,"H":0,"physical_units":3,"codes":6,"fake_regulatory_sscc":False,"native_putaway_done":True,"birth_replay_exact":True}))
