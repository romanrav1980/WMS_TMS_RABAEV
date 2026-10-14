"""383 existing small-case departed load to original weight/photo receipt; synthetic equipment."""
import io,sys,json
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,oracledb
from PIL import Image
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:8];sender="QS383"+tag;receiver="QR383"+tag
secret=uuid4().hex;groups=["SG383"+tag.upper(),"RG383"+tag.upper()]
admin=httpx.Client(auth=("admin","admin123"),timeout=30);gateway=httpx.Client(auth=(sender,secret),timeout=30);shop=httpx.Client(auth=(receiver,secret),timeout=30)
base="http://127.0.0.1:8088";load="SMALL211.LOAD:8258e0ab"
def stamp(x):return x.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:p_op and ACTIVE_FLAG=1",p_op=load)
 addresses={r[0]for r in q.fetchall()};assert len(addresses)==1;address=addresses.pop()
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 for actor,group in zip((sender,receiver),groups):
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:p_actor,:p_secret,'Own383 software receiver',:p_group,0,0)",p_actor=actor,p_secret=secret,p_group=group)
 c.commit()
 try:
  for group,right in zip(groups,("store_scale_ingest","store_receipt_confirm")):
   call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own383 scale receipt"})
   call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own383 software case"})
  call(admin,"POST","/api/delivery/store-receipts/receivers",{"store_address":address,"username":receiver})
  device="STORE383:"+tag;ref="SYNTHETIC383:"+tag
  call(admin,"PUT","/api/delivery/store-scales/devices/"+device,{"store_address":address,"sender_id":sender,"expected_version":0,"active":True,"capacity_kg":"100","resolution_kg":"0.000000001","calibration_ref":ref,"calibrated_until":stamp(datetime.now(timezone.utc)+timedelta(days=1))})
  preview=call(shop,"GET","/api/delivery/store-receipts/preview?load_operation_id="+load+"&store_address="+address.replace(" ","%20"))
  assert preview["mode"]=="WEIGHT_PHOTO"and not preview["already_received"]and preview["requires_marked_recipient_flow"]
  assert preview["shipping_gross_weight_kg"]=="1.45"and preview["shipping_weight_tolerance_kg"]=="0.225"
  assert preview["physical_boxes"][0]["gross_weight_kg"]=="0.45"and preview["physical_boxes"][0]["device_mode"]=="TEST"
  assert preview["marked_unit_control"]["supported"]and preview["marked_unit_control"]["physical_unit_count"]==7 and preview["marked_unit_control"]["expected_scan_count"]==14,preview
  from app.modules.platform.public import read_oracle_json
  source={"case":1112,"load_operation_id":load}
  q.execute("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1112");lot=q.fetchone()[0]
  q.execute("select PHYSICAL_UNIT_KEY,UNIT_ID,UID_PALLET from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot and STOCK_STATUS='ISSUED'order by UNIT_ID",lot=lot);members=q.fetchall();assert len(members)==7
  scans=[]
  for index,(key,unit_id,birth)in enumerate(members[:5]):
   disposition="ACCEPTED"if index<3 else "REFUSED"if index==3 else "DAMAGED"
   q.execute("select SYSTEM_CODE,RAW_CODE,PROFILES_JSON from RRL_WMS_RECEIPT_CODE where UID_PALLET=:birth and UNIT_ID=:unit_id order by SYSTEM_CODE",birth=birth,unit_id=unit_id)
   for system,raw,profiles in q.fetchall():
    code=raw.read()if hasattr(raw,"read")else raw
    for profile in read_oracle_json(profiles):scans.append(dict(system_code=system,profile_code=profile["profile"],code=code,disposition=disposition))
  assert len(scans)==10
  photos=[]
  for i,view in enumerate(("FRONT","LEFT","RIGHT")):
   image=Image.new("RGB",(320,240),(30+i*60,100,40));out=io.BytesIO();image.save(out,format="PNG")
   r=shop.post(base+"/api/delivery/store-photos/upload",params={"load_operation_id":load,"store_address":address,"view":view},content=out.getvalue(),headers={"Content-Type":"image/png"})
   assert r.status_code==200,(r.status_code,r.text[:1000]);photos.append(r.json()["photo_id"])
  def capture(weight):
   now=datetime.now(timezone.utc)
   body={"device_id":device,"capture_id":"SW383:"+uuid4().hex,"load_operation_id":load,"store_address":address,"device_policy_version":1,"calibration_ref":ref,"unit":"KG","basis":"GROSS","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=40)),"measured_at":stamp(now),"samples":[{"offset_ms":i*500,"gross_weight_kg":weight}for i in range(5)]}
   return call(gateway,"POST","/api/delivery/store-scales/captures",body)["capture_key"]
  body={"operation_id":"STORE383.RECEIPT:"+tag,"load_operation_id":load,"store_address":address,"scan_place":preview["root_scan_identifier"],"expected_composition_signature":preview["composition_signature"],"before_cameras":True,"photo_ids":photos,"scale_capture_key":capture("1.45"),"scans":scans,
        "observations":[{"lot_uid":lot,"accepted":"3","missing":"2","refused":"1","damaged":"1","extra":"0"}],"case_note":"Own synthetic CASE partial receipt: three accepted, two absent, one refused, one damaged"}
  wrong=[dict(x)for x in scans];wrong[1]["disposition"]="REFUSED"
  denied=call(shop,"POST","/api/delivery/store-receipts/confirm",{**body,"operation_id":"STORE383.CONFLICT:"+tag,"scans":wrong},status=409)
  assert "STORE_MARK_ONE_UNIT_DISPOSITION_REQUIRED"in denied["detail"]["message"],denied
  from app.modules.inventory.public import StockCommand,normalize_unit_scan_codes
  from app.modules.platform.public import read_oracle_json
  meta={key:value for key,value in body.items()if key not in("operation_id","load_operation_id","store_address","scans")}
  meta["unit_scans"]=normalize_unit_scan_codes(scans)
  trial="STORE383.ROLL:"+tag
  wire=StockCommand(operation_id=trial,command_type="STORE_RECEIPT",actor=receiver,source={"load_operation_id":load,"store_address":address},metadata=meta,lines=()).canonical_json()
  c.commit();out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[wire,receiver,out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op",op=trial);assert q.fetchone()==(7,7)
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()[0]==0
  Path("tmp/progress383.json").write_text(json.dumps({"body":body,"source":source,"receiver_id":receiver,"sender_id":sender}),encoding="utf-8")
  result=call(shop,"POST","/api/delivery/store-receipts/confirm",body)
  assert result["status"]=="DISCREPANCY"and result["weight"]["tolerance_kg"]=="0.225"and result["weight"]["delta_kg"]=="0"
  assert sum(int(x["accepted_quantity"])for x in result["accepted_lines"])==3
  assert call(shop,"POST","/api/delivery/store-receipts/confirm",body)==result
  assert not result["warehouse_stock_consumed_again"]and not result["government_ack_created"]
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_EVENT_OUTBOX where CORRELATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select count(*)from RRL_STORE_RECEIPT_WEIGHT_PHOTO where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==3
  q.execute("select count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(7,7)
  q.execute("select CUSTOMER_ORDER_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=source["case"]);order=q.fetchone()[0]
  from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
  from app.oracle_gateway import OracleGateway
  delivery=OrderDelivery(OracleGateway()).get(int(order));assert delivery["quantities"][0]["accepted"]=="3",delivery
  q.execute("select UNIT_DISPOSITION,count(*),sum(BASE_QTY)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op group by UNIT_DISPOSITION order by UNIT_DISPOSITION",op=body["operation_id"]);assert q.fetchall()==[("ACCEPTED",3,3),("DAMAGED",1,1),("MISSING",2,2),("REFUSED",1,1)]
  Path("tmp/context383.json").write_text(json.dumps({"source":source,"receipt_body":body,"result":result,"order_delivery":delivery,"receiver_id":receiver,"actors_retired_after_case":True},indent=2),encoding="utf-8")
  print("PASS383 actual oldmarkedCASE7 ->accepted3/missing2/refused1/damaged1/10QR of5present/oneunitconflict denied/nativewhole rollback/nonadmin3photos/replay/oneoutbox/no stock/no GovACK",load,body["operation_id"],flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID in(:p_sender,:p_receiver)",p_sender=sender,p_receiver=receiver);c.commit()
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
