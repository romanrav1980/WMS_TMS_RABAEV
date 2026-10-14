import sys,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];source="STORE.RECEIPT:04633c677f";base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(client,method,path,body=None,status=200,raw=None):
 r=client.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}));assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("""select line.LINE_NO,line.LOT_UID,line.ARTICLE,line.BASE_UOM,f.TT_ID,f.VEHICLE_ID,f.VEHICLE_NUMBER,tt.VODITEL_ID,
 r.STORE_ADDR,f.WARE_ID,p.EXPIRY_DATE,a.BARCODE_SHT,w.DEFAULT_RECEIVE_CELL,pol.DISPOSAL_RECEIVE_CELL
 from RRL_STORE_RECEIPT_LINE line join RRL_STORE_RECEIPT_FACT r on r.OPERATION_ID=line.OPERATION_ID
 join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID join RRL_TRANSPORT_TASK tt on tt.ID=f.TT_ID
 join RRL_PALLETS p on p.UID_PALLET=line.LOT_UID join RRL_ARTICULS a on a.ACTICUL=line.ARTICLE
 join RRL_WARES w on w.ID=f.WARE_ID left join RRL_STORE_RETURN_WARE_POLICY pol on pol.WARE_ID=f.WARE_ID
 where line.OPERATION_ID=:source""",source=source)
 line,lot,article,uom,trip,vehicle,plate,driver,store,ware,expiry,barcode,sap_cell,cell=q.fetchone()
 def config(sql,**values):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,values);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 if not sap_cell or not cell:
  sap_cell="QDG"+tag;cell="QDD"+tag;supplier_cell="QDS"+tag
  for target in [sap_cell,cell,supplier_cell]:
   blocked=0 if target==sap_cell else 1
   config("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,:blocked,:blocked,0,100,0)",cell=target,ware=ware,blocked=blocked)
   config("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target)
  config("update RRL_WARES set DEFAULT_RECEIVE_CELL=:cell where ID=:ware",cell=sap_cell,ware=ware)
  call(admin,"PUT",f"/api/inventory/store-returns/warehouses/{ware}/policy",{"supplier_receive_cell":supplier_cell,"disposal_receive_cell":cell,"expected_version":0})
 approval={"operation_id":"DISPOSAL.APPROVE:"+tag,"line_no":int(line),"quantity":"1","disposition":"DISPOSAL","reason":"Own defect destruction fixture","decision_reference":"SC:"+tag,"complete_good_box":False}
 call(admin,"POST","/api/delivery/store-returns/"+source+"/approve",approval)
 root=ET.Element("WarehouseStoreReturn",version="1")
 values={"Sender":"OWN.QA.SAP","MessageId":"DISPOSAL.RETURN:"+tag,"ReturnDocumentNumber":"DISPOSAL.RTN:"+tag,"ApprovalOperationId":approval["operation_id"],"OriginalReceiptOperationId":source,"OriginalLineNumber":str(line),"WarehouseId":str(ware),"ReceiveCell":sap_cell,"Article":article,"LotId":lot,"Quantity":"1","Disposition":"DISPOSAL"}
 for name,value in values.items():ET.SubElement(root,name,**({"unit":uom}if name=="Quantity"else{})).text=value
 call(admin,"POST","/api/integrations/sap/store-returns",status=202,raw=ET.tostring(root,encoding="utf-8"))
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=20,PALLETS=4 where ID=:id",id=vehicle);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 plan={"operation_id":"DISPOSAL.TR.PLAN:"+tag,"approval_operation_id":approval["operation_id"],"task_id":int(trip),"gross_weight_kg":"2","physical_places":1}
 call(admin,"POST","/api/delivery/store-return-transport/plan",plan)
 handed={"operation_id":"DISPOSAL.HAND:"+tag,"transport_operation_id":plan["operation_id"],"pallet_identifier":"DISPOSAL.RETURN:"+tag,"quantity":"1","base_uom":uom,"gross_weight_kg":"2","physical_places":1}
 call(admin,"POST","/api/delivery/store-return-custody/handover",handed)
 actor="QDX"+tag;group=actor.upper();secret=uuid4().hex
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own disposal driver',:grp,0,0)",id=actor,secret=secret,grp=group);c.commit()
 call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own disposal driver"})
 call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"driver_return_accept","description":"Own physical return pickup"})
 old=call(admin,"GET",f"/api/transport/driver-bindings/{driver}");assert not old["active"]
 bound=call(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":True,"expected_version":old["binding_version"]})
 try:
  driver_client=httpx.Client(auth=(actor,secret),timeout=35)
  pickup={"operation_id":"DISPOSAL.PICK:"+tag,"handover_operation_id":handed["operation_id"],"scan_vehicle":plate,"scan_pallet":handed["pallet_identifier"]}
  call(driver_client,"POST","/api/delivery/store-return-custody/pickup",pickup)
  body={"operation_id":"DISPOSAL.RECEIVE:"+tag,"pickup_operation_id":pickup["operation_id"],"scan_pallet":handed["pallet_identifier"],"scan_vehicle":plate,"scan_cell":cell,"scan_article":barcode,"article":article,"quantity":"1","base_uom":uom,"expiry_date":expiry.strftime("%Y-%m-%d"),"supplier_batch":"OWN.OBSERVED.DISPOSAL:"+tag,"gross_weight_kg":"2","net_weight_kg":"1.5"}
  received=call(admin,"POST","/api/inventory/store-returns/receive",body);assert call(admin,"POST","/api/inventory/store-returns/receive",body)==received
  print("PASS110 fresh ordinary DISPOSAL source1 original store/SAP/driver/blocked receipt; tag="+tag+" receipt="+body["operation_id"],flush=True)
 finally:
  call(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":False,"expected_version":bound["binding_version"]})
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
