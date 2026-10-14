from pathlib import Path
import json,re
s=Path("scripts/ni053_store_barcode_case.py").read_text(encoding="utf-8-sig")
s=re.sub(r'(?<![A-Za-z0-9_])3(?![A-Za-z0-9_])','24',s).replace("0.125","1")
needle=' q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET=\'DS-BASE-B1\'");article=q.fetchone()[0]'
replacement=''' import httpx,xml.etree.ElementTree as ET
 client=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def fullapi(method,path,body=None,status=200,raw=None):
  response=client.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}))
  assert response.status_code==status,(response.status_code,response.text[:1800]);return response.json()
 article="REUSE.QA:"+tag;barcode="REUSE.EA:"+tag;box_barcode="REUSE.BOX:"+tag;batch="REUSE.BATCH:"+tag
 prefix=str(30000000000000000+int(tag[:8],16));digit=(10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10;lot=prefix+str(digit)
 idoc=ET.Element("ARTMAS10");document=ET.SubElement(idoc,"IDOC");control=ET.SubElement(document,"EDI_DC40")
 def fields(node,values):
  for name,value in values.items():ET.SubElement(node,name).text=str(value)
 fields(control,{"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","DOCNUM":str(1000000000000000+int(tag[:8],16)),"SNDPRN":"OWN.QA.SAP","CREDAT":"20261010","CRETIM":"090000"})
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",{"BASE_UOM":"EA","EAN_UPC":barcode}),("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":"Own full box reuse "+tag}),("E1BPE1MARMRT",{"ALT_UNIT":"EA","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":barcode}),("E1BPE1MARMRT",{"ALT_UNIT":"BOX","NUMERATOR":"24","DENOMINATR":"1","EAN_UPC":box_barcode})]:
  fields(ET.SubElement(document,segment),{"MATERIAL":article,**values})
 fullapi("POST","/api/integrations/sap/artmas",status=202,raw=ET.tostring(idoc,encoding="utf-8"))
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","finished_goods_edit"])
 try:q.execute("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:article,1,0,'admin')",article=article);conn.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
'''
assert needle in s;s=s.replace(needle,replacement,1)
needle=' revision=int(q.callfunc'
at=s.index(needle)
s=s[:at]+''' receive_cell="QIN"+tag;pick_cell="QIP"+tag
 for cell,pick in [(receive_cell,0),(pick_cell,1)]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,:pick,0,0,0)",cell=cell,pick=pick)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 meta("update RRL_WARES set DEFAULT_RECEIVE_CELL=:cell where ID=:ware",cell=receive_cell)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX)values(:ware,:article,:cell,0,0)",article=article,cell=pick_cell)
 supply=ET.Element("WarehouseSupplyOrder",version="1")
 fields(supply,{"Sender":"OWN.QA.SAP","MessageId":"REUSE.SUPPLY:"+tag,"OrderNumber":"REUSE:"+tag,"Revision":"1","WarehouseId":ware,"ReceiveCell":receive_cell,"Supplier":"Own software fixture"})
 line_node=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line_node,{"LineNumber":"1","Material":article});ET.SubElement(line_node,"Quantity",unit="EA").text="24"
 imported=fullapi("POST","/api/integrations/sap/supply-orders",status=202,raw=ET.tostring(supply,encoding="utf-8"));supply_id=imported["order_id"]
'''+s[at:]
old='   post("INVENTORY_REGISTER_LOT",{"uid":u,"cell":cell,"article":article,"quantity":"24","expiry_date":"2030-01-01","price":0,"reason":"Full-pallet binding fixture"},{"revision_id":revision})'
new='''   if u==lot:
    payload={"operation_id":"REUSE.SAP.RECEIVE:"+tag,"line_number":"1","sscc":lot,"quantity":"24","product_barcode":box_barcode,"supplier_batch":batch,"expiry_date":"2030-01-01","gross_weight":"10","units":[],"aggregations":[]}
    incoming=fullapi("POST",f"/api/receiving/supply-orders/{supply_id}/pallets",payload,201)
    assert incoming["putaway_cell"]==src,incoming
    fullapi("POST",f"/api/receiving/putaway/{incoming['task_id']}/complete",{"scanned_pallet":lot,"scanned_from_cell":receive_cell,"scanned_to_cell":src})
   else:post("INVENTORY_REGISTER_LOT",{"uid":u,"cell":cell,"article":article,"quantity":"24","expiry_date":"2030-01-01","price":0,"reason":"Full-pallet binding fixture"},{"revision_id":revision})'''
assert old in s;s=s.replace(old,new,1)
# Retain successful physical flow, omit old unrelated store-policy regression tail.
begin=s.index('  for suffix,changed,rule in(');end=s.index('  accepted=http("POST","/confirm",receipt)',begin);s=s[:begin]+s[end:]
begin=s.index('  conflict=http(');end=s.index(' finally:',begin)
s=s[:begin]+'''  print("PASS107 fresh assumed ARTMAS/warehouse SAP receipt BOX24/original verified batch -> existing whole picking/ST/nested load/departure/store acceptance24; tag="+tag,flush=True)
'''+s[end:]
print(json.dumps({"scripts/ni062_reuse_source_case.py":s},ensure_ascii=True))
