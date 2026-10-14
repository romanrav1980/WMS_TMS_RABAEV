exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx,xml.etree.ElementTree as ET
from uuid import uuid4
ctx=json.loads(Path("tmp/context642.json").read_text());origin=ctx["source"];source=ctx["receipt_operation_id"];ware=origin["warehouse"];tag=origin["tag"]
p=Path("tmp/context643.json");saved=json.loads(p.read_text())if p.exists()else{"source":ctx,"tag":tag}
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
def call(client,method,path,body=None,status=200,raw=None):
 r=client.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}));assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def config(fn):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:fn();c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 cells=["QS643"+tag,"QD643"+tag,"QR643"+tag]
 if "zones"not in saved:
  for cell in cells:
   def create():
    q.execute("select count(*)from RRL_CELLS where CELL=:cell",cell=cell)
    if not q.fetchone()[0]:
     q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,1,1,0,100,0)",cell=cell,ware=ware)
     q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
   config(create)
  call(admin,"PUT",f"/api/inventory/store-returns/warehouses/{ware}/policy",{"supplier_receive_cell":cells[0],"disposal_receive_cell":cells[1],"expected_version":0})
  call(admin,"PUT",f"/api/inventory/store-returns/warehouses/{ware}/reuse-receiving",{"receive_cell":cells[2],"expected_version":1})
  saved["zones"]=cells;save()
 scans=[code for unit in origin["units"]for code in unit["codes"]]
 aggregation_scans=[dict(system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=origin["lot"]),dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]
 scans=[]
 if "source_modes_set"not in saved:
  def modes():
   q.execute("update RRL_SKU_RECEIPT_PROFILE set SCAN_MODE=case SYSTEM_CODE when 'CRPT'then 'PALLET'else 'BOX'end where ARTICUL=:article",article=origin["article"])
  config(modes);saved["source_modes_set"]=True;save()
 q.execute("select PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op and UNIT_DISPOSITION='ACCEPTED'order by PHYSICAL_UNIT_KEY",op=source);keys=[x[0]for x in q];assert len(keys)==3
 approval={"operation_id":"REUSE643.APPROVE:"+tag,"line_no":1,"quantity":"3","disposition":"REUSE","reason":"Own original complete marked BOX3 returned","decision_reference":"DEV643:"+tag,"complete_good_box":True,"unit_keys":keys}
 if "approval"not in saved:saved["approval"]=call(admin,"POST","/api/delivery/store-returns/"+source+"/approve",approval);save()
 if "sap"not in saved:
  root=ET.Element("WarehouseStoreReturn",version="1")
  values={"Sender":"OWN.QA.SAP","MessageId":"REUSE643.SAP:"+tag,"ReturnDocumentNumber":"REUSE643:"+tag,"ApprovalOperationId":approval["operation_id"],"OriginalReceiptOperationId":source,"OriginalLineNumber":"1","WarehouseId":str(ware),"ReceiveCell":origin["receive"],"Article":origin["article"],"LotId":origin["lot"],"Quantity":"3","Disposition":"REUSE"}
  for name,value in values.items():ET.SubElement(root,name,**({"unit":"EA"}if name=="Quantity"else{})).text=value
  saved["sap"]=call(admin,"POST","/api/integrations/sap/store-returns",status=202,raw=ET.tostring(root,encoding="utf-8"));save()
 if "capacity"not in saved:
  config(lambda:q.execute("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=20,PALLETS=2 where ID=:id",id=origin["vehicle"]));saved["capacity"]=True;save()
 plan={"operation_id":"REUSE643.TR:"+tag,"approval_operation_id":approval["operation_id"],"task_id":origin["source_trip"],"gross_weight_kg":"2","physical_places":1}
 if "plan"not in saved:saved["plan"]=call(admin,"POST","/api/delivery/store-return-transport/plan",plan);save()
 uid=origin["lot"];hand={"operation_id":"REUSE643.HAND:"+tag,"transport_operation_id":plan["operation_id"],"pallet_identifier":uid,"quantity":"3","base_uom":"EA","gross_weight_kg":"2","physical_places":1,"scans":scans,"aggregation_scans":aggregation_scans}
 if "handover"not in saved:
  all_units=[code for unit in origin["units"]for code in unit["codes"]]
  call(admin,"POST","/api/delivery/store-return-custody/handover",{**hand,"operation_id":hand["operation_id"]+".BAD.UNIT","aggregation_scans":[],"scans":all_units},409)
  call(admin,"POST","/api/delivery/store-return-custody/handover",{**hand,"operation_id":hand["operation_id"]+".BAD.IDENTITY","pallet_identifier":"REPACK643:"+tag},409)
  saved["handover"]=call(admin,"POST","/api/delivery/store-return-custody/handover",hand);save()
 actor="QD643"+tag;group=actor.upper()
 q.execute("select PASS,NAME from RUSERS where ID=:actor",actor=actor);row=q.fetchone()
 if row:secret,name=row;assert name=="Own643 return driver";q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=actor);c.commit()
 else:secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:actor,:secret,'Own643 return driver',:grp,0,0)",actor=actor,secret=secret,grp=group);c.commit()
 call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own643 driver"})
 call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"driver_return_accept","description":"Own exact marked return pickup"})
 driver=origin["driver"]
 current=call(admin,"GET",f"/api/transport/driver-bindings/{driver}")
 if "original_binding"not in saved:assert not current["active"];saved["original_binding"]=current;save()
 if not(current["active"]and current.get("user_id")==actor):current=call(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":True,"expected_version":current["binding_version"]})
 try:
  with httpx.Client(auth=(actor,secret),timeout=40)as driver_client:
   pickup={"operation_id":"REUSE643.PICK:"+tag,"handover_operation_id":hand["operation_id"],"scan_vehicle":origin["plate"],"scan_pallet":uid,"scans":scans,"aggregation_scans":aggregation_scans}
   if "pickup"not in saved:saved["pickup"]=call(driver_client,"POST","/api/delivery/store-return-custody/pickup",pickup);save()
  body={"operation_id":"REUSE643.RECEIVE:"+tag,"pickup_operation_id":pickup["operation_id"],"scan_pallet":uid,"scan_vehicle":origin["plate"],"scan_cell":cells[2],"scan_article":origin["box_barcode"],"article":origin["article"],"quantity":"3","base_uom":"EA","expiry_date":origin["expiry"],"supplier_batch":origin["supplier_batch"],"gross_weight_kg":"2","net_weight_kg":"1.5","full_box_count":"1","complete_good_boxes":True,"scans":scans,"aggregation_scans":aggregation_scans}
  if "receipt"not in saved:
   call(admin,"POST","/api/inventory/store-returns/receive",{**body,"operation_id":"REUSE643.BAD:"+tag,"full_box_count":"2"},409)
   saved["receipt"]=call(admin,"POST","/api/inventory/store-returns/receive",body);saved["receipt_body"]=body;save()
  assert call(admin,"POST","/api/inventory/store-returns/receive",saved["receipt_body"])==saved["receipt"]
  if "placement"not in saved:saved["placement"]=call(admin,"POST","/api/inventory/store-return-putaway/plan",{"operation_id":"REUSE643.PUT:"+tag,"receipt_operation_id":body["operation_id"]});save()
  task=saved["placement"]["task_id"];target=saved["placement"]["to_cell"];assert target==origin["pick"],saved["placement"]
  if "done"not in saved:
   call(admin,"POST",f"/api/warehouse-tasks/{task}/assign",{"assigned_to":"admin"})
   call(admin,"POST",f"/api/warehouse-tasks/{task}/start",{})
   completion={"operation_id":"REUSE643.DONE:"+tag,"scanned_pallet":uid,"scanned_from_cell":cells[2],"scanned_to_cell":target,"fact_qty":"3"}
   saved["done"]=call(admin,"POST",f"/api/warehouse-tasks/{task}/complete",completion);saved["done_body"]=completion;save()
  assert call(admin,"POST",f"/api/warehouse-tasks/{task}/complete",saved["done_body"])==saved["done"]
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=target);assert q.fetchone()==(3,0)
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=uid);assert q.fetchone()==(3,3)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:lot",lot=origin["lot"]);assert q.fetchone()[0]==6
  q.execute("select RRL_STOCK_ELIGIBILITY.reason(:p_uid,:cell,:ware,1,null,null,'ALLOCATE')from dual",p_uid=uid,cell=target,ware=ware);assert q.fetchone()[0]is None
  saved["returned_uid"]=uid;saved["available_physical_quantity"]="3";save()
 finally:
  latest=call(admin,"GET",f"/api/transport/driver-bindings/{driver}")
  if latest.get("user_id")==actor:
   old=saved["original_binding"];call(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":old.get("user_id")or actor,"active":bool(old.get("active")),"expected_version":latest["binding_version"]})
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit()
print("PASS643 preserved original PALLET identity / CRPT PALLET-only + EGAIS BOX-only; existing markedREUSE sourceSAPverifiedBOX3/3oldkeys6QR/approval-SAP-plan-handover-driverpickup/blockedreceipt/nativeputaway/available3H0/no rebirth/replay")
