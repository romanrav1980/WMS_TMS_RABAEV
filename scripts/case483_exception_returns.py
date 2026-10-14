exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,xml.etree.ElementTree as ET
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from app.modules.platform.public import read_oracle_json
p=Path("tmp/context483.json");seed=json.loads(Path("tmp/check477.out").read_text(encoding="utf-16").splitlines()[-1])
saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else dict(receipt=seed["receipt"],source=seed["source"],selected=seed["selected"],tag="c09bc5c0")
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def call(method,path,body=None,status=200,raw=None,client=admin):
 r=client.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}))
 assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def config(fn):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:fn();c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("""select load.WARE_ID,w.NAME,w.DEFAULT_RECEIVE_CELL,tt.ID,tt.VODITEL_ID,v.ID,v.NUM,v.PALLETS,v.MAX_WEIGHT_KG
 from RRL_STORE_RECEIPT_FACT f join RRL_TT_HU_LOAD_FACT load on load.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
 join RRL_WARES w on w.ID=load.WARE_ID join RRL_TRANSPORT_TASK tt on tt.ID=load.TT_ID
 join RRL_TR_VEHICLE v on v.NUM=tt.TRANSPORT where f.OPERATION_ID=:op""",op=saved["receipt"])
 ware,name,receive,trip,driver,vehicle,plate,places,mass=q.fetchone()
 assert name=="Own180 8258e0ab"and plate=="QV2118258e0ab",(name,plate)
 line=saved["source"]["lines"][0];article=line["article"];lot=line["lot_uid"];tag=saved["tag"]
 # Retained QA item GTIN is shared with other QA articles. Use its own existing
 # box barcode; preserve GS1 codes and the strict unique barcode resolver.
 barcode="QBOX483"+tag
 config(lambda:q.execute("update RRL_ARTICULS set BARCODE_KOR=:bc where ACTICUL=:a",bc=barcode,a=article))
 q.execute("select to_char(p.EXPIRY_DATE,'YYYY-MM-DD'),r.SUPPLIER_BATCH from RRL_PALLETS p join RRL_SAP_PALLET_RECEIPT r on r.UID_PALLET=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET)where p.UID_PALLET=:p_uid",p_uid=lot)
 expiry,batch=q.fetchone()

 if "zones"not in saved:
  zones=["QS483"+tag,"QD483"+tag]
  for cell in zones:
   def create():
    q.execute("select count(*)from RRL_CELLS where CELL=:cell",cell=cell)
    if q.fetchone()[0]==0:
     q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,1,1,1,0,100,0)",cell=cell,ware=ware)
     q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
   config(create)
  policy=call("GET",f"/api/inventory/store-returns/warehouses/{ware}/policy")
  call("PUT",f"/api/inventory/store-returns/warehouses/{ware}/policy",dict(supplier_receive_cell=zones[0],disposal_receive_cell=zones[1],expected_version=policy.get("policy_version",0)))
  config(lambda:q.execute("update RRL_TR_VEHICLE set PALLETS=4,MAX_WEIGHT_KG=100 where ID=:v",v=vehicle))
  saved["zones"]=zones;save()
 if "approvals"not in saved:
  common=dict(line_no=line["line_no"],quantity="1",disposition="SUPPLIER",return_basis="REFUSED",reason="Physical goods refused at delivery",decision_reference="DEV483:unaccepted-goods",unit_keys=saved["selected"]["REFUSED"],complete_good_box=False)
  bodies=[dict(common,operation_id="EXRET483.REF:"+tag+"."+suffix)for suffix in ["A","B"]]
  def submit(body):
   with httpx.Client(auth=("admin","admin123"),timeout=40)as client:
    return client.post(base+"/api/delivery/store-returns/"+saved["receipt"]+"/approve",json=body)
  with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(submit,bodies))
  assert sorted(r.status_code for r in responses)==[200,409],[r.text for r in responses]
  i=next(i for i,r in enumerate(responses)if r.status_code==200)
  saved["approvals"]={"REFUSED":responses[i].json()};saved["approval_bodies"]={"REFUSED":bodies[i]};save()
 if "DAMAGED"not in saved["approvals"]:
  body=dict(operation_id="EXRET483.DAM:"+tag,line_no=line["line_no"],quantity="1",disposition="DISPOSAL",return_basis="DAMAGED",reason="Physical goods damaged at delivery",decision_reference="DEV483:damaged-goods",unit_keys=saved["selected"]["DAMAGED"],complete_good_box=False)
  saved["approvals"]["DAMAGED"]=call("POST","/api/delivery/store-returns/"+saved["receipt"]+"/approve",body);saved["approval_bodies"]["DAMAGED"]=body;save()
 actor="QD483"+tag;group=actor.upper()
 q.execute("select PASS from RUSERS where ID=:actor",actor=actor);row=q.fetchone()
 if row:secret=row[0];q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=actor);c.commit()
 else:
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:actor,:secret,'Own483 exception-return driver',:grp,0,0)",actor=actor,secret=secret,grp=group);c.commit()
 call("POST","/api/admin/rights/groups",dict(id=group,name="Own483 driver"))
 call("POST",f"/api/admin/rights/groups/{group}/rights",dict(right_name="driver_return_accept",description="Own483 physical exception return"))
 current=call("GET",f"/api/transport/driver-bindings/{driver}")
 if "original_binding"not in saved:saved["original_binding"]=current;save()
 if not(current["active"]and current.get("user_id")==actor):call("PUT",f"/api/transport/driver-bindings/{driver}",dict(user_id=actor,active=True,expected_version=current["binding_version"]))
 try:
  with httpx.Client(auth=(actor,secret),timeout=40)as driver_client:
   for basis,destination,cell in [("REFUSED","SUPPLIER",saved["zones"][0]),("DAMAGED","DISPOSAL",saved["zones"][1])]:
    part=saved.setdefault(basis,{});approval=saved["approvals"][basis]["operation_id"];uid="EXRET483:"+basis+":"+tag
    scans=[]
    for key in saved["selected"][basis]:
     q.execute("select code.SYSTEM_CODE,code.PROFILES_JSON from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE code on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID where u.PHYSICAL_UNIT_KEY=:k",k=key)
     for system,profiles in q:
      for profile in read_oracle_json(profiles):scans.append(dict(system_code=system,profile_code=profile["profile"],code=profile["raw_code"]))
    assert len(scans)==2,scans
    if "sap"not in part:
     def xml(version,message):
      root=ET.Element("WarehouseStoreReturn",version=str(version))
      values={"Sender":"OWN.QA.SAP","MessageId":message,"ReturnDocumentNumber":"EXRET483:"+basis+":"+tag,"ApprovalOperationId":approval,"OriginalReceiptOperationId":saved["receipt"],"OriginalLineNumber":"1","WarehouseId":str(ware),"ReceiveCell":receive,"Article":article,"LotId":lot,"Quantity":"1","Disposition":destination}
      if version==2:values["OriginalReceiptDisposition"]=basis
      for name,value in values.items():ET.SubElement(root,name,**({"unit":"EA"}if name=="Quantity"else{})).text=value
      return ET.tostring(root,encoding="utf-8")
     call("POST","/api/integrations/sap/store-returns",raw=xml(1,"EXRET483.BAD:"+basis+":"+tag),status=409)
     part["sap"]=call("POST","/api/integrations/sap/store-returns",raw=xml(2,"EXRET483.SAP:"+basis+":"+tag),status=202);save()
    if "plan"not in part:
     part["plan"]=call("POST","/api/delivery/store-return-transport/plan",dict(operation_id="EXRET483.TR:"+basis+":"+tag,approval_operation_id=approval,task_id=trip,gross_weight_kg="0.25",physical_places=1));save()
    if "handover"not in part:
     part["handover"]=call("POST","/api/delivery/store-return-custody/handover",dict(operation_id="EXRET483.HAND:"+basis+":"+tag,transport_operation_id=part["plan"]["operation_id"],pallet_identifier=uid,quantity="1",base_uom="EA",gross_weight_kg="0.25",physical_places=1,scans=scans));save()
    if "pickup"not in part:
     part["pickup"]=call("POST","/api/delivery/store-return-custody/pickup",dict(operation_id="EXRET483.PICK:"+basis+":"+tag,handover_operation_id=part["handover"]["operation_id"],scan_vehicle=plate,scan_pallet=uid,scans=scans),client=driver_client);save()
    if "receipt"not in part:
     body=dict(operation_id="EXRET483.RECEIVE3:"+basis+":"+tag,pickup_operation_id=part["pickup"]["operation_id"],scan_pallet=uid,scan_vehicle=plate,scan_cell=cell,scan_article=barcode,article=article,quantity="1",base_uom="EA",expiry_date=expiry,supplier_batch=batch,gross_weight_kg="0.25",net_weight_kg="0.05",scans=scans)
     part["receipt"]=call("POST","/api/inventory/store-returns/receive",body);part["receipt_body"]=body;save()
    assert call("POST","/api/inventory/store-returns/receive",part["receipt_body"])==part["receipt"]
    q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=cell);assert q.fetchone()==(1,0)
    q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and STOCK_STATUS='AVAILABLE'",p_uid=uid);assert q.fetchone()==(1,1)
  source=call("GET","/api/delivery/store-returns/"+saved["receipt"]);line_now=source["lines"][0]
  assert line_now["accepted_quantity"]=="3"and line_now["available_for_approval"]=="3"and line_now["refused_available"]=="0"and line_now["damaged_available"]=="0",line_now
  q.execute("select ACCEPTED_BASE_QTY,MISSING_BASE_QTY,REFUSED_BASE_QTY,DAMAGED_BASE_QTY from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op",op=saved["receipt"]);assert q.fetchone()==(3,2,1,1)
  saved["result"]="WAREHOUSE_RETURNED_REFUSED1_DAMAGED1_BUYER_ACCEPTED3_UNCHANGED";save()
 finally:
  latest=call("GET",f"/api/transport/driver-bindings/{driver}")
  if latest.get("user_id")==actor:
   old=saved["original_binding"];call("PUT",f"/api/transport/driver-bindings/{driver}",dict(user_id=old.get("user_id")or actor,active=bool(old.get("active")),expected_version=latest["binding_version"]))
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit()
print("PASS483 REFUSED1+DAMAGED1 existing approval/SAPv2/originaltrip/handover/bounddriver/warehousequarantine P1each samekeys/2QR each/replay; concurrent refused cap one winner; buyer3 and acceptedreturncap3 unchanged")
