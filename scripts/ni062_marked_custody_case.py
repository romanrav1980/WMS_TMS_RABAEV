import sys,json
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
s=get_settings();tag="13508027ed";approval="RET231.LEGACY:"+tag;store_actor="SR229"+tag;driver_actor="DR233"+tag
base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=40)
def api(h,method,path,body=None,status=200):
 r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select a.RECEIPT_OPERATION_ID,a.LINE_NO,a.LOT_UID,a.ARTICLE,a.BASE_UOM,a.BASE_QTY,a.DISPOSITION,l.TT_ID,l.VEHICLE_NUMBER,tt.VODITEL_ID from RRL_STORE_RETURN_APPROVAL a join RRL_STORE_RECEIPT_FACT r on r.OPERATION_ID=a.RECEIPT_OPERATION_ID join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID join RRL_TRANSPORT_TASK tt on tt.ID=l.TT_ID where a.OPERATION_ID=:p",p=approval)
 receipt,line,uid,article,uom,qty,disposition,trip,plate,driver=q.fetchone();ware=51365792;cell="QR233"+tag
 def cfg(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select count(*)from RRL_CELLS where CELL=:p",p=cell)
 if not q.fetchone()[0]:
  cfg("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:p,:w,0,0,0,0,0,0,0,0,1,1)",p=cell,w=ware)
  cfg("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p=cell)
 cfg("update RRL_WARES set DEFAULT_RECEIVE_CELL=:p where ID=:w",p=cell,w=ware)
 values={"Sender":"OWN.QA.SAP","MessageId":"RET233."+tag,"ReturnDocumentNumber":"OWN.RET233."+tag,"ApprovalOperationId":approval,"OriginalReceiptOperationId":receipt,"OriginalLineNumber":str(line),"WarehouseId":str(ware),"ReceiveCell":cell,"Article":article,"LotId":uid,"Quantity":str(int(qty)),"Disposition":disposition}
 root=ET.Element("WarehouseStoreReturn",version="1")
 for name,value in values.items():ET.SubElement(root,name,**({"unit":uom}if name=="Quantity"else{})).text=value
 raw=ET.tostring(root,encoding="utf-8",xml_declaration=True)
 r=admin.post(base+"/api/integrations/sap/store-returns",content=raw,headers={"Content-Type":"application/xml"});assert r.status_code==202,(r.status_code,r.text)
 transport="RET233.PLAN:"+tag;planned=api(admin,"POST","/api/delivery/store-return-transport/plan",{"operation_id":transport,"approval_operation_id":approval,"task_id":int(trip),"gross_weight_kg":"2","physical_places":1})
 assert planned["physical_pickup_confirmed"]is False
 q.execute("select MAX_WEIGHT_KG,PALLETS from RRL_TR_VEHICLE where NUM=:p",p=plate);assert q.fetchone()==(100,1)
 q.execute("select PASS,USER_GROUP from RUSERS where ID=:p",p=store_actor);store_secret,group=q.fetchone()
 api(admin,"POST","/api/admin/rights/groups/"+group+"/rights",{"right_name":"store_return_handover","description":"Own233 exact marked return"})
 q.execute("select PASS from RUSERS where ID=:p",p=driver_actor);row=q.fetchone()
 if row:secret=row[0]
 else:
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p,:s,'Own233 dedicated return driver',:g,:w,0,0)",p=driver_actor,s=secret,g=driver_actor.upper(),w=ware);c.commit()
 api(admin,"POST","/api/admin/rights/groups/"+driver_actor.upper()+"/rights",{"right_name":"driver_return_accept","description":"Own233 exact marked return"})
 binding=api(admin,"GET","/api/transport/driver-bindings/"+str(driver));bound=api(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":driver_actor,"active":True,"expected_version":binding["binding_version"]})
 store=httpx.Client(auth=(store_actor,store_secret),timeout=40);dc=httpx.Client(auth=(driver_actor,secret),timeout=40)
 q.execute("select x.SYSTEM_CODE,x.PROFILES_JSON,x.RAW_CODE from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY join RRL_WMS_RECEIPT_CODE x on x.UID_PALLET=u.UID_PALLET and x.UNIT_ID=u.UNIT_ID where b.APPROVAL_OPERATION_ID=:p order by x.SYSTEM_CODE",p=approval);scans=[]
 for system,profiles,code in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":code.read()if hasattr(code,"read")else code})
 assert len(scans)==2
 path="/api/delivery/store-return-custody"
 rows=api(store,"GET",path+"/store?store_address=Own%20full-pallet%20ST&task_id="+str(trip));row=next(x for x in rows if x["transport_operation_id"]==transport);assert row["marked_unit_control"]["expected_scan_count"]==2
 hand={"operation_id":"RET233.HAND:"+tag,"transport_operation_id":transport,"pallet_identifier":"RETURN233:"+tag,"quantity":"1","base_uom":uom,"gross_weight_kg":"2","physical_places":1,"scans":scans}
 api(store,"POST",path+"/handover",dict(hand,operation_id="RET233.HAND.MISSING:"+tag,scans=scans[:1]),409)
 api(store,"POST",path+"/handover",dict(hand,operation_id="RET233.HAND.DUP:"+tag,scans=[scans[0],scans[0]]),409)
 def rollback(kind,body,actor,source_name):
  metadata={k:v for k,v in body.items()if k not in("operation_id",source_name,"scans")};metadata["unit_scans"]=normalize_unit_scan_codes(body["scans"])
  cmd={"contract_version":2,"operation_id":body["operation_id"]+".ROLLBACK","command_type":kind,"actor":actor,"source":{source_name:body[source_name]},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(cmd),actor,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 rollback("STORE_RETURN_HANDOVER",hand,store_actor,"transport_operation_id")
 q.execute("select count(*)from RRL_STORE_RETURN_HANDOVER where TRANSPORT_OPERATION_ID=:p",p=transport);assert q.fetchone()[0]==0
 def run(i):
  body=dict(hand,operation_id=hand["operation_id"]+str(i))
  with httpx.Client(auth=(store_actor,store_secret),timeout=40)as h:return h.post(base+path+"/handover",json=body),body
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,[0,1]))
 assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:3000])for r,b in results]
 saved,hand=next((r.json(),b)for r,b in results if r.status_code==200);assert saved["physical_unit_count"]==1 and saved["mark_scan_confirmed"]
 assert api(store,"POST",path+"/handover",hand)==saved
 pickup={"operation_id":"RET233.PICKUP:"+tag,"handover_operation_id":hand["operation_id"],"scan_vehicle":plate,"scan_pallet":hand["pallet_identifier"],"scans":scans}
 rows=api(dc,"GET",path+"/driver?task_id="+str(trip));row=next(x for x in rows if x["handover_operation_id"]==hand["operation_id"]);assert row["marked_unit_control"]["expected_scan_count"]==2
 api(dc,"POST",path+"/pickup",dict(pickup,operation_id="RET233.PICKUP.MISSING:"+tag,scans=scans[:1]),409)
 api(admin,"POST",path+"/pickup",pickup,403)
 rollback("STORE_RETURN_PICKUP",pickup,driver_actor,"handover_operation_id")
 picked=api(dc,"POST",path+"/pickup",pickup);assert picked["custody"]=="VEHICLE"and picked["physical_unit_count"]==1
 assert api(dc,"POST",path+"/pickup",pickup)==picked
 off=api(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":driver_actor,"active":False,"expected_version":bound["binding_version"]})
 try:api(dc,"POST",path+"/pickup",pickup,403)
 finally:api(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":driver_actor,"active":True,"expected_version":off["binding_version"]})
 assert api(dc,"POST",path+"/pickup",pickup)==picked
 for op in[hand["operation_id"],pickup["operation_id"]]:
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=op);assert q.fetchone()[0]==0
 q.execute("select count(*),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p and STOCK_STATUS='ISSUED'",p=uid);assert q.fetchone()==(3,10,10)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS233 original SAP return binding/released outbound allows backhaul without changing100kg-1pallet/exact approved original1unit-2QR/store and dedicated driver/native rollback/concurrent handover winner/replay/current binding403/no stock/protected20-20",hand["operation_id"],pickup["operation_id"],flush=True)
