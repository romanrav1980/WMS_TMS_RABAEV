import sys,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];source="STORE.RECEIPT:cdbf4c0962";base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(client,method,path,body=None,status=200,raw=None):
 r=client.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}));assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("""select line.LINE_NO,line.LOT_UID,line.ARTICLE,line.BASE_UOM,line.ACCEPTED_BASE_QTY,f.TT_ID,f.VEHICLE_ID,f.VEHICLE_NUMBER,tt.VODITEL_ID,r.STORE_ADDR,f.WARE_ID,p.EXPIRY_DATE,sap.SUPPLIER_BATCH,a.BARCODE_KOR,w.DEFAULT_RECEIVE_CELL
 from RRL_STORE_RECEIPT_LINE line join RRL_STORE_RECEIPT_FACT r on r.OPERATION_ID=line.OPERATION_ID join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
 join RRL_TRANSPORT_TASK tt on tt.ID=f.TT_ID join RRL_PALLETS p on p.UID_PALLET=line.LOT_UID join RRL_SAP_PALLET_RECEIPT sap on sap.UID_PALLET=p.UID_PALLET join RRL_ARTICULS a on a.ACTICUL=line.ARTICLE join RRL_WARES w on w.ID=f.WARE_ID
 where line.OPERATION_ID=:source""",source=source)
 line,lot,article,uom,qty,trip,vehicle,plate,driver,store,ware,expiry,batch,barcode,sap_cell=q.fetchone();assert qty==24 and batch and barcode
 def config(sql,**values):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,values);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 cells=["QRSU"+tag,"QRDI"+tag,"QRRE"+tag]
 for cell in cells:
  config("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,1,1,0,100,0)",cell=cell,ware=ware)
  config("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 p="/api/inventory/store-returns"
 call(admin,"PUT",p+f"/warehouses/{ware}/policy",{"supplier_receive_cell":cells[0],"disposal_receive_cell":cells[1],"expected_version":0})
 call(admin,"PUT",p+f"/warehouses/{ware}/reuse-receiving",{"receive_cell":cells[2],"expected_version":1})
 approval={"operation_id":"REUSE.APPROVE:"+tag,"line_no":int(line),"quantity":"24","disposition":"REUSE","reason":"Own original full good box returned","decision_reference":"SC:"+tag,"complete_good_box":True}
 call(admin,"POST","/api/delivery/store-returns/"+source+"/approve",approval)
 root=ET.Element("WarehouseStoreReturn",version="1")
 values={"Sender":"OWN.QA.SAP","MessageId":"REUSE.RETURN:"+tag,"ReturnDocumentNumber":"REUSE.RTN:"+tag,"ApprovalOperationId":approval["operation_id"],"OriginalReceiptOperationId":source,"OriginalLineNumber":str(line),"WarehouseId":str(ware),"ReceiveCell":sap_cell,"Article":article,"LotId":lot,"Quantity":"24","Disposition":"REUSE"}
 for name,value in values.items():ET.SubElement(root,name,**({"unit":uom}if name=="Quantity"else{})).text=value
 call(admin,"POST","/api/integrations/sap/store-returns",status=202,raw=ET.tostring(root,encoding="utf-8"))
 config("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=20,PALLETS=2 where ID=:id",id=vehicle)
 plan={"operation_id":"REUSE.TR.PLAN:"+tag,"approval_operation_id":approval["operation_id"],"task_id":int(trip),"gross_weight_kg":"2","physical_places":1}
 call(admin,"POST","/api/delivery/store-return-transport/plan",plan)
 handed={"operation_id":"REUSE.HAND:"+tag,"transport_operation_id":plan["operation_id"],"pallet_identifier":"REUSE.RETURN:"+tag,"quantity":"24","base_uom":uom,"gross_weight_kg":"2","physical_places":1}
 call(admin,"POST","/api/delivery/store-return-custody/handover",handed)
 actor="QRX"+tag;group=actor.upper();secret=uuid4().hex
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own reuse return driver',:grp,0,0)",id=actor,secret=secret,grp=group);c.commit()
 call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own reuse driver"})
 call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"driver_return_accept","description":"Own physical return pickup"})
 old=call(admin,"GET",f"/api/transport/driver-bindings/{driver}");assert not old["active"]
 bound=call(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":True,"expected_version":old["binding_version"]})
 try:
  driver_client=httpx.Client(auth=(actor,secret),timeout=35)
  pickup={"operation_id":"REUSE.PICK:"+tag,"handover_operation_id":handed["operation_id"],"scan_vehicle":plate,"scan_pallet":handed["pallet_identifier"]}
  call(driver_client,"POST","/api/delivery/store-return-custody/pickup",pickup)
  body={"operation_id":"REUSE.RECEIVE:"+tag,"pickup_operation_id":pickup["operation_id"],"scan_pallet":handed["pallet_identifier"],"scan_vehicle":plate,"scan_cell":cells[2],"scan_article":barcode,"article":article,"quantity":"24","base_uom":uom,"expiry_date":expiry.strftime("%Y-%m-%d"),"supplier_batch":batch,"gross_weight_kg":"2","net_weight_kg":"1.5","full_box_count":"1","complete_good_boxes":True}
  call(admin,"POST",p+"/receive",{**body,"operation_id":"REUSE.BAD.BOX:"+tag,"full_box_count":"2"},409)
  result=call(admin,"POST",p+"/receive",body);assert call(admin,"POST",p+"/receive",body)==result
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=handed["pallet_identifier"],cell=cells[2]);assert q.fetchone()==(24,0)
  q.execute("select BOX_COUNT,BOX_BASE_QTY,SOURCE_BATCH from RRL_RETURN_REUSE_PROOF where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,24,batch)
  placed_plan={"operation_id":"REUSE.PUT.PLAN:"+tag,"receipt_operation_id":body["operation_id"]}
  created=call(admin,"POST","/api/inventory/store-return-putaway/plan",placed_plan);task=created["task_id"]
  assert call(admin,"POST","/api/inventory/store-return-putaway/plan",placed_plan)==created
  target=created["to_cell"];assert target=="QIPcdbf4c0962"
  taskpath=f"/api/warehouse-tasks/{task}"
  call(admin,"POST",taskpath+"/assign",{"assigned_to":"admin"});call(admin,"POST",taskpath+"/start",{})
  completion={"operation_id":"REUSE.PUT.COMPLETE:"+tag,"scanned_pallet":handed["pallet_identifier"],"scanned_from_cell":cells[2],"scanned_to_cell":target,"fact_qty":"24"}
  completed=call(admin,"POST",taskpath+"/complete",completion);assert call(admin,"POST",taskpath+"/complete",completion)==completed
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell",lot_id=handed["pallet_identifier"],cell=target);assert q.fetchone()==(24,0)
  q.execute("select RRL_STOCK_ELIGIBILITY.reason(:lot_id,:cell,:ware,1,null,null,'ALLOCATE')from dual",lot_id=handed["pallet_identifier"],cell=target,ware=ware);assert q.fetchone()==(None,)
  q.execute("select count(*)from RRL_STORE_RETURN_PLACEMENT where RECEIPT_OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  print("PASS107 actual approved BOX24/original verified SAP batch/current bound driver/blocked receipt24/proof1x24 -> existing task/picking24 H0/eligible/replay/original trace; tag="+tag,flush=True)
  q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_RETURN_REUSE_PROOF%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
 finally:
  call(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":False,"expected_version":bound["binding_version"]})
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
