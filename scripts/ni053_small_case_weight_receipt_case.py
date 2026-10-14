"""208 existing small-case departed load to original weight/photo receipt; synthetic equipment."""
import io,sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,oracledb
from PIL import Image
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:8];sender="QS208"+tag;receiver="QR208"+tag
secret=uuid4().hex;groups=["SG208"+tag.upper(),"RG208"+tag.upper()]
admin=httpx.Client(auth=("admin","admin123"),timeout=30);gateway=httpx.Client(auth=(sender,secret),timeout=30);shop=httpx.Client(auth=(receiver,secret),timeout=30)
base="http://127.0.0.1:8088";load=sys.argv[1]if len(sys.argv)>1 else "SMALL207.LOAD:5ab68dd7"
def stamp(x):return x.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:p_op and ACTIVE_FLAG=1",p_op=load)
 addresses={r[0]for r in q.fetchall()};assert len(addresses)==1;address=addresses.pop()
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 for actor,group in zip((sender,receiver),groups):
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:p_actor,:p_secret,'Own208 software receiver',:p_group,0,0)",p_actor=actor,p_secret=secret,p_group=group)
 c.commit()
 try:
  for group,right in zip(groups,("store_scale_ingest","store_receipt_confirm")):
   call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own208 scale receipt"})
   call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own208 software case"})
  call(admin,"POST","/api/delivery/store-receipts/receivers",{"store_address":address,"username":receiver})
  device="STORE208:"+tag;ref="SYNTHETIC208:"+tag
  call(admin,"PUT","/api/delivery/store-scales/devices/"+device,{"store_address":address,"sender_id":sender,"expected_version":0,"active":True,"capacity_kg":"100","resolution_kg":"0.000000001","calibration_ref":ref,"calibrated_until":stamp(datetime.now(timezone.utc)+timedelta(days=1))})
  preview=call(shop,"GET","/api/delivery/store-receipts/preview?load_operation_id="+load+"&store_address="+address.replace(" ","%20"))
  assert preview["mode"]=="WEIGHT_PHOTO"and not preview["already_received"]and not preview["requires_marked_recipient_flow"]
  assert preview["shipping_gross_weight_kg"]=="1.4"and preview["shipping_weight_tolerance_kg"]=="0.2"
  assert preview["physical_boxes"][0]["gross_weight_kg"]=="0.4"and preview["physical_boxes"][0]["device_mode"]=="TEST"
  photos=[]
  for i,view in enumerate(("FRONT","LEFT","RIGHT")):
   image=Image.new("RGB",(320,240),(30+i*60,100,40));out=io.BytesIO();image.save(out,format="PNG")
   r=shop.post(base+"/api/delivery/store-photos/upload",params={"load_operation_id":load,"store_address":address,"view":view},content=out.getvalue(),headers={"Content-Type":"image/png"})
   assert r.status_code==200,(r.status_code,r.text[:1000]);photos.append(r.json()["photo_id"])
  def capture(weight):
   now=datetime.now(timezone.utc)
   body={"device_id":device,"capture_id":"SW208:"+uuid4().hex,"load_operation_id":load,"store_address":address,"device_policy_version":1,"calibration_ref":ref,"unit":"KG","basis":"GROSS","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=40)),"measured_at":stamp(now),"samples":[{"offset_ms":i*500,"gross_weight_kg":weight}for i in range(5)]}
   return call(gateway,"POST","/api/delivery/store-scales/captures",body)["capture_key"]
  body={"operation_id":"STORE208.RECEIPT:"+tag,"load_operation_id":load,"store_address":address,"scan_place":preview["root_scan_identifier"],"expected_composition_signature":preview["composition_signature"],"before_cameras":True,"photo_ids":photos,"scale_capture_key":capture("1.199999999")}
  refused=call(shop,"POST","/api/delivery/store-receipts/confirm",body,status=409);assert "STORE_WEIGHT_ACT_REQUIRED"in refused["detail"]["message"]
  q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:p_op",p_op=load);assert q.fetchone()[0]==0
  body["scale_capture_key"]=capture("1.2")
  result=call(shop,"POST","/api/delivery/store-receipts/confirm",body)
  assert result["status"]=="ACCEPTED"and result["weight"]["tolerance_kg"]=="0.2"and result["weight"]["delta_kg"]=="-0.2"
  assert sum(int(x["accepted_quantity"])for x in result["accepted_lines"])==6
  assert call(shop,"POST","/api/delivery/store-receipts/confirm",body)==result
  assert not result["warehouse_stock_consumed_again"]and not result["government_ack_created"]
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_EVENT_OUTBOX where CORRELATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select count(*)from RRL_STORE_RECEIPT_WEIGHT_PHOTO where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==3
  print("PASS208 existing departed measuredCASE6/.400 + outer1=1.4, nonadmin store actual synthetic1.2 inclusive .2 tolerance, epsilon refused, 3 original views, accepted6/replay/outbox1/no quantity journal/no second stock/no government ACK",load,body["operation_id"],flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID in(:p_sender,:p_receiver)",p_sender=sender,p_receiver=receiver);c.commit()
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
