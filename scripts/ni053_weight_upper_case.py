"""New own prepared place: unique original photos and inclusive upper boundary."""
import io,sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,oracledb
from PIL import Image
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();source_tag=sys.argv[1];tag=uuid4().hex[:10];sender="QUP"+tag;group="QU"+tag.upper();password=uuid4().hex
addr="STORE.QA:"+source_tag;load="FULL.HU.SHIP:"+source_tag;device="DEV.UPPER:"+tag
admin=httpx.Client(auth=("admin","admin123"),timeout=30);gw=httpx.Client(auth=(sender,password),timeout=30);base="http://127.0.0.1:8088"
def stamp(t):return t.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1000]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own upper weight gateway',:grp,0,0)",id=sender,secret=password,grp=group);conn.commit()
 try:
  call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own upper gateway"})
  call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"store_scale_ingest","description":"Own upper weight case"})
  now=datetime.now(timezone.utc);ref="DEV.UPPER:"+tag
  call(admin,"PUT","/api/delivery/store-scales/devices/"+device,{"store_address":addr,"sender_id":sender,"expected_version":0,"active":True,"capacity_kg":"100","resolution_kg":"0.000000001","calibration_ref":ref,"calibrated_until":stamp(now+timedelta(days=1))})
  preview=call(admin,"GET",f"/api/delivery/store-receipts/preview?load_operation_id={load}&store_address={addr}")
  assert not preview["already_received"]
  photos=[];front=None
  for index,view in enumerate(("FRONT","LEFT","RIGHT")):
   output=io.BytesIO();Image.new("RGB",(320,240),(index*50,80,90)).save(output,format="PNG");image=output.getvalue()
   if index==0:front=image
   r=admin.post(base+"/api/delivery/store-photos/upload",params={"load_operation_id":load,"store_address":addr,"view":view},content=image,headers={"Content-Type":"image/png"})
   assert r.status_code==200,(r.status_code,r.text[:600]);photos.append(r.json()["photo_id"])
  r=admin.post(base+"/api/delivery/store-photos/upload",params={"load_operation_id":load,"store_address":addr,"view":"BACK"},content=front,headers={"Content-Type":"image/png"});assert r.status_code==200;reused=r.json()["photo_id"]
  now=datetime.now(timezone.utc)
  packet={"device_id":device,"capture_id":"UP:"+tag,"load_operation_id":load,"store_address":addr,"device_policy_version":1,"calibration_ref":ref,"unit":"KG","basis":"GROSS","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"-0.000000001","zero_check_at":stamp(now-timedelta(seconds=20)),"measured_at":stamp(now),"samples":[{"offset_ms":i*500,"gross_weight_kg":"11"} for i in range(5)]}
  capture=call(gw,"POST","/api/delivery/store-scales/captures",packet)
  body={"operation_id":"STORE.UPPER:"+tag,"load_operation_id":load,"store_address":addr,"scan_place":preview["root_scan_identifier"],"expected_composition_signature":preview["composition_signature"],"before_cameras":True,"scale_capture_key":capture["capture_key"],"photo_ids":photos}
  rejected=call(admin,"POST","/api/delivery/store-receipts/confirm",{**body,"operation_id":"UP.BAD.PHOTO:"+tag,"photo_ids":[photos[0],reused,photos[2]]},status=409)
  assert "STORE_WEIGHT_DISTINCT_ORIGINAL_PHOTOS_REQUIRED" in rejected["detail"]["message"],rejected
  result=call(admin,"POST","/api/delivery/store-receipts/confirm",body)
  assert result["status"]=="ACCEPTED" and result["weight"]["delta_kg"]=="1" and result["weight"]["in_tolerance"]==1
  assert call(admin,"POST","/api/delivery/store-receipts/confirm",body)==result
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(0,)
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  print("PASS089 actual upper11/source10/half-box1 inclusive acceptance, signed zero, same original image under different view refused, exact replay/outbox1/no second quantity")
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=sender);conn.commit()
