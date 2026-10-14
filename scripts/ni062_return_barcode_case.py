"""Fresh existing-source return2: shared ordinary barcode resolver and actual stock commit."""
import sys,json
from pathlib import Path
from uuid import uuid4
import xml.etree.ElementTree as ET
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
admin=httpx.Client(auth=("admin","admin123"),timeout=30)
username,group,password="QRB"+tag,"QRB"+tag.upper(),uuid4().hex
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor();q.execute("""
 select a.OPERATION_ID,a.RECEIPT_OPERATION_ID,a.LINE_NO,a.LOT_UID,a.ARTICLE,a.BASE_UOM,to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),a.DISPOSITION,
 f.TT_ID,f.VEHICLE_ID,f.VEHICLE_NUMBER,tt.VODITEL_ID,r.STORE_ADDR,to_char(original.EXPIRY_DATE,'YYYY-MM-DD'),card.BARCODE_SHT
 from RRL_STORE_RETURN_APPROVAL a join RRL_STORE_RECEIPT_FACT r on r.OPERATION_ID=a.RECEIPT_OPERATION_ID
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
 join RRL_TRANSPORT_TASK tt on tt.ID=f.TT_ID
 join RRL_PALLETS original on original.UID_PALLET=a.LOT_UID
 join RRL_ARTICULS card on card.ACTICUL=a.ARTICLE
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:04633c677f' and a.DISPOSITION='SUPPLIER'
 """)
 approval,receipt,line,lot,article,uom,qty,disposition,trip,vehicle,plate,driver,store,expiry,barcode=q.fetchone();assert qty=="2" and barcode
 q.execute("select DEFAULT_RECEIVE_CELL from RRL_WARES where ID=9104");sap_cell=q.fetchone()[0]
 q.execute("select SUPPLIER_RECEIVE_CELL from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=9104");receive_cell=q.fetchone()[0]
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own return barcode driver',:grp,0,0)",id=username,secret=password,grp=group);c.commit()
 version=None
 try:
  call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own return barcode driver"})
  call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"driver_return_accept","description":"Own author source driver"})
  driver_client=httpx.Client(auth=(username,password),timeout=30)
  old=call(admin,"GET","/api/transport/driver-bindings/"+str(driver))
  binding=call(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":username,"active":True,"expected_version":old["binding_version"]});version=binding["binding_version"]
  values={"Sender":"OWN.QA.SAP","MessageId":"BARCODE."+tag,"ReturnDocumentNumber":"OWN.BARCODE."+tag,"ApprovalOperationId":approval,"OriginalReceiptOperationId":receipt,"OriginalLineNumber":str(line),"WarehouseId":"9104","ReceiveCell":sap_cell,"Article":article,"LotId":lot,"Quantity":qty,"Disposition":disposition}
  root=ET.Element("WarehouseStoreReturn",version="1")
  for name,value in values.items():
   node=ET.SubElement(root,name,**({"unit":uom} if name=="Quantity" else {}));node.text=value
  raw=ET.tostring(root,encoding="utf-8",xml_declaration=True)
  response=admin.post(base+"/api/integrations/sap/store-returns",content=raw,headers={"Content-Type":"application/xml"});assert response.status_code==202,(response.status_code,response.text[:800])
  q.execute("select nvl(sum(GROSS_WEIGHT_KG),0),count(*) from RRL_TT_HU_LOAD_FACT where TT_ID=:trip and STATUS in('LOADED','DEPARTED')",trip=trip);loaded,places=q.fetchone()
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=:cap,PALLETS=:places where ID=:vehicle",cap=loaded+2,places=places+1,vehicle=vehicle);c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
  plan={"operation_id":"RETURN.BAR.PLAN:"+tag,"approval_operation_id":approval,"task_id":int(trip),"gross_weight_kg":"2","physical_places":1}
  call(admin,"POST","/api/delivery/store-return-transport/plan",plan)
  handed={"operation_id":"RETURN.BAR.HAND:"+tag,"transport_operation_id":plan["operation_id"],"pallet_identifier":"RETURN.PHYS:"+tag,"quantity":qty,"base_uom":uom,"gross_weight_kg":"2","physical_places":1}
  call(admin,"POST","/api/delivery/store-return-custody/handover",handed)
  pickup={"operation_id":"RETURN.BAR.PICK:"+tag,"handover_operation_id":handed["operation_id"],"scan_vehicle":plate,"scan_pallet":handed["pallet_identifier"]}
  call(driver_client,"POST","/api/delivery/store-return-custody/pickup",pickup)
  body={"operation_id":"RETURN.BAR.RECEIVE:"+tag,"pickup_operation_id":pickup["operation_id"],"scan_pallet":handed["pallet_identifier"],"scan_vehicle":plate,"scan_cell":receive_cell,
        "scan_article":barcode,"article":article,"quantity":qty,"base_uom":uom,"expiry_date":expiry,"supplier_batch":"OBSERVED.BAR."+tag,"gross_weight_kg":"2","net_weight_kg":"1.5"}
  bad=call(admin,"POST","/api/inventory/store-returns/receive",{**body,"operation_id":"RETURN.BAR.BAD:"+tag,"scan_article":"FOREIGN."+tag},409);assert "QUALITY_FOREIGN_ITEM_BARCODE" in bad["detail"]["message"],bad
  domain={"legs":[{"article":article,"base_uom":uom,"quantity":"2"}]}
  scans={"item_scans":[{"barcode":barcode,"scan_id":"BAR1."+tag,"quantity":"1"},{"barcode":barcode,"scan_id":"BAR2."+tag,"quantity":"1"}]}
  q.callproc("RRL_STOCK_QC_ITEM.validate_scan",[json.dumps(domain),json.dumps(scans)]);c.rollback()
  result=call(admin,"POST","/api/inventory/store-returns/receive",body);assert result["quantity"]=="2" and not result["available_for_reservation"] and result["document_kind"]=="STORE_RETURN"
  assert call(admin,"POST","/api/inventory/store-returns/receive",body)==result
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=handed["pallet_identifier"],cell=receive_cell);assert q.fetchone()==(2,0)
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  print("PASS096 fresh existing source2/SAP/plan/store+bound driver/actual shared barcode/foreign barcode refusal/QC same resolver/typed return document/blocked P2H0/replay/event1/outbox1",flush=True)
 finally:
  if version is not None:call(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":username,"active":False,"expected_version":version})
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=username);c.commit()
