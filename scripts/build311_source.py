from pathlib import Path
import json
p=Path("scripts/source311_marked_case.py");t=Path("scripts/source310_marked_case.py").read_text(encoding="utf-8").replace("310","311")
needle='with oracledb.connect(user=cfg.oracle_user'
i=t.index(needle)
t=t[:i]+'''lot_prefix=str(50000000000000000+int(tag,16))
lot=lot_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(lot_prefix)))%10)%10)
'''+t[i:]
a=t.index('  ctx=api("POST","/api/inventory/trace-manifests/inventory-context"');b=t.index('\n  post("RESERVATION_CREATE"',a)
t=t[:a]+'''  import xml.etree.ElementTree as ET
  receive="QR311"+tag;pick="QK311"+tag
  for cell,is_pick in [(receive,0),(pick,1)]:
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:ware,0,0,0,:pick,0,0,0)",c=cell,pick=is_pick)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
  meta("update RRL_WARES set DEFAULT_RECEIVE_CELL=:cell where ID=:ware",cell=receive)
  meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,SOURCE_PICK_MODE)values(:ware,:a,:cell,0,'AFTER_PUTAWAY')",a=article,cell=pick)
  sscc_prefix="100"+str(int(tag,16)).zfill(14)
  sscc=sscc_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(sscc_prefix)))%10)%10)
  scan_aggregations=[dict(system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=sscc),dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]
  supply=ET.Element("WarehouseSupplyOrder",version="1")
  def fields(node,values):
   for key,value in values.items():ET.SubElement(node,key).text=str(value)
  fields(supply,dict(Sender="OWN.QA.SAP",MessageId="IW311.SUPPLY:"+tag,OrderNumber="IW311:"+tag,Revision=1,WarehouseId=ware,ReceiveCell=receive,Supplier="Own311 exact SAP source"))
  line=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line,dict(LineNumber="1",Material=article));ET.SubElement(line,"Quantity",unit="EA").text="3"
  containers=ET.SubElement(supply,"Aggregations")
  for aggregation in scan_aggregations:
   item=ET.SubElement(containers,"Aggregation")
   fields(item,dict(LineNumber="1",System=aggregation["system_code"],Profile=aggregation["profile_code"],Level=aggregation["level"],Code=aggregation["code"]))
   members=ET.SubElement(item,"Units")
   for unit in units:
    code=next(code["code"]for code in unit["codes"]if code["system_code"]==aggregation["system_code"])
    fields(ET.SubElement(members,"Unit"),dict(UnitId=unit["unit_id"],Quantity="1",Code=code))
  imported=admin_api.post(base+"/api/integrations/sap/supply-orders",content=ET.tostring(supply,encoding="utf-8"),headers={"Content-Type":"application/xml"});assert imported.status_code==202,imported.text
  order_id=imported.json()["order_id"];manifest_op=None
  born=api("POST","/api/receiving/supply-orders/"+order_id+"/pallets",dict(operation_id="IW311.BIRTH:"+tag,line_number="1",sscc=lot,quantity="3",supplier_batch="PB311:"+tag,expiry_date="2030-01-01",gross_weight="3",units=[],aggregations=scan_aggregations),status=201)
  assert born["putaway_cell"]==src,born
  api("POST","/api/receiving/putaway/"+str(born["task_id"])+"/complete",dict(scanned_pallet=lot,scanned_from_cell=receive,scanned_to_cell=src))
'''+t[b:]
t=t.replace('"manifest_operation_id":manifest_op}', '"manifest_operation_id":manifest_op,"sap_order_id":order_id}')
print(json.dumps({p.as_posix():t}))
