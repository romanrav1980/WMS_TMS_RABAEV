"""Actual Oracle/HTTP software admission with synthetic samples/photos; no hardware claim."""
import io,json,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from PIL import Image
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];sender="QWS"+tag;receiver="QWR"+tag;sg="QG"+tag.upper();rg="QR"+tag.upper()
sp,rp=uuid4().hex,uuid4().hex;admin=httpx.Client(auth=("admin","admin123"),timeout=30);gw=httpx.Client(auth=(sender,sp),timeout=30);shop=httpx.Client(auth=(receiver,rp),timeout=30)
base="http://127.0.0.1:8088";receipt_base="/api/delivery/store-receipts";scale_base="/api/delivery/store-scales"
def stamp(value):return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1500]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor()
 for user,password,group in ((sender,sp,sg),(receiver,rp,rg)):
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own weight admission actor',:grp,0,0)",id=user,secret=password,grp=group)
 conn.commit()
 try:
  for group,right in ((sg,"store_scale_ingest"),(rg,"store_receipt_confirm")):
   call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own weight admission"})
   call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own admission case"})
  def setup(source_tag):
   load="FULL.HU.SHIP:"+source_tag;addr="STORE.QA:"+source_tag;device="DEV.WEIGHT:"+tag+":"+source_tag
   call(admin,"POST",receipt_base+"/receivers",{"store_address":addr,"username":receiver})
   policy={"store_address":addr,"sender_id":sender,"expected_version":0,"active":True,"capacity_kg":"100","resolution_kg":"0.000000001","calibration_ref":"DEV.SYNTHETIC:"+tag,"calibrated_until":stamp(datetime.now(timezone.utc)+timedelta(days=1))}
   call(admin,"PUT",scale_base+"/devices/"+device,policy)
   preview=call(shop,"GET",receipt_base+f"/preview?load_operation_id={load}&store_address={addr}")
   assert preview["mode"]=="WEIGHT_PHOTO" and preview["shipping_weight_tolerance_kg"]=="1" and not preview["already_received"]
   photos=[]
   for index,view in enumerate(("FRONT","LEFT","RIGHT")):
    image=Image.new("RGB",(320,240),(index*70,40,130));out=io.BytesIO();image.save(out,format="PNG")
    response=shop.post(base+"/api/delivery/store-photos/upload",params={"load_operation_id":load,"store_address":addr,"view":view},content=out.getvalue(),headers={"Content-Type":"image/png"})
    assert response.status_code==200,(response.status_code,response.text[:900]);photos.append(response.json()["photo_id"])
   def capture(weight):
    now=datetime.now(timezone.utc)
    packet={"device_id":device,"capture_id":"W:"+uuid4().hex,"load_operation_id":load,"store_address":addr,"device_policy_version":1,"calibration_ref":policy["calibration_ref"],"unit":"KG","basis":"GROSS","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=40)),"measured_at":stamp(now),"samples":[{"offset_ms":i*500,"gross_weight_kg":weight} for i in range(5)]}
    return call(gw,"POST",scale_base+"/captures",packet)["capture_key"]
   body={"operation_id":"STORE.WEIGHT:"+tag+":"+source_tag,"load_operation_id":load,"store_address":addr,"scan_place":preview["root_scan_identifier"],"expected_composition_signature":preview["composition_signature"],"before_cameras":True,"photo_ids":photos}
   leaf=next(node for node in preview["snapshot"]["nodes"] if node["kind"]=="STOCK")
   counts=[{"lot_uid":leaf["uid"],"accepted":"3","missing":"0","refused":"0","damaged":"0","extra":"0"}]
   return body,counts,capture
  body,counts,capture=setup("20a98330c0")
  low_out=capture("8.999999999");body["scale_capture_key"]=low_out
  for label,change,rule,status in (
   ("OUTSIDE",{},"STORE_WEIGHT_ACT_REQUIRED",409),
   ("ACT.EMPTY",{"weight_act_confirmed":True},"STORE_WEIGHT_REPRESENTATIVE_REQUIRED",403),
   ("ACT.ROLE",{"weight_act_confirmed":True,"observations":counts,"case_note":"Own verified discrepancy"},"STORE_WEIGHT_REPRESENTATIVE_REQUIRED",403),
   ("PHOTOS",{"photo_ids":body["photo_ids"][:2]},"STORE_WEIGHT_PHOTO_BOUND_3_12",409),
   ("DUP.PHOTO",{"photo_ids":[body["photo_ids"][0]]*3},"STORE_WEIGHT_PHOTO_DUPLICATE",409)):
   rejected=call(shop,"POST",receipt_base+"/confirm",{**body,**change,"operation_id":"WEIGHT.BAD."+label+":"+tag},status=status)
   assert rule in rejected["detail"]["message"],rejected
  refused=call(admin,"POST",receipt_base+"/confirm",{**body,"operation_id":"WEIGHT.BAD.COUNTS:"+tag,"weight_act_confirmed":True,"case_note":"Own act"},status=409)
  assert "STORE_WEIGHT_ACT_COUNTS_AND_REASON_REQUIRED" in refused["detail"]["message"],refused
  body["scale_capture_key"]=capture("9")
  accepted=call(shop,"POST",receipt_base+"/confirm",body)
  assert accepted["status"]=="ACCEPTED" and accepted["weight"]["delta_kg"]=="-1" and accepted["weight"]["in_tolerance"]==1,accepted
  assert accepted["weight"]["tolerance_kg"]=="1" and accepted["accepted_lines"][0]["accepted_quantity"]=="3"
  assert call(shop,"POST",receipt_base+"/confirm",body)==accepted
  q.execute("select IN_TOLERANCE,ACT_CONFIRMED,DELTA_KG,TOLERANCE_KG from RRL_STORE_RECEIPT_WEIGHT where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,0,-1,1)
  print("PASS089 actual non-admin receiver weight9/source10/half actual box1 inclusive lower boundary/three original views/replay; epsilon outside/act rights/counts/missing/duplicate photo refused",flush=True)
  second,second_counts,second_capture=setup("22c5dc5ec4")
  second.update(scale_capture_key=second_capture("11.000000001"),weight_act_confirmed=True,observations=second_counts,case_note="Own representative act: checked full quantities; mass differs")
  acted=call(admin,"POST",receipt_base+"/confirm",second)
  assert acted["status"]=="DISCREPANCY" and acted["weight"]["in_tolerance"]==0 and acted["weight"]["act_confirmed"]==1,acted
  assert acted["weight"]["delta_kg"]=="1.000000001" and acted["accepted_lines"][0]["accepted_quantity"]=="3"
  assert acted["discrepancy_case_id"]==second["operation_id"] and call(admin,"POST",receipt_base+"/confirm",second)==acted
  for request in (body,second):
   op=request["operation_id"]
   q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
   q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=op);assert q.fetchone()==(1,)
   q.execute("select count(*) from RRL_STORE_RECEIPT_WEIGHT_PHOTO where OPERATION_ID=:op",op=op);assert q.fetchone()==(3,)
  q.execute("select STATUS from RRL_STORE_DISCREPANCY_CASE where CASE_ID=:op",op=second["operation_id"]);assert q.fetchone()==("OPEN",)
  q.execute("select count(*) from RRL_STORE_DELIVERY_OBLIGATION where CASE_ID=:op",op=second["operation_id"]);assert q.fetchone()==(0,)
  try:q.execute("delete RRL_STORE_RECEIPT_WEIGHT where OPERATION_ID=:op",op=body["operation_id"]);conn.commit();raise AssertionError("Weight evidence deleted")
  except oracledb.DatabaseError as exc:conn.rollback();assert "STORE_WEIGHT_EVIDENCE_IMMUTABLE" in str(exc)
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=sender);conn.commit()
  assert call(shop,"POST",receipt_base+"/confirm",body)==accepted
  assert not acted["warehouse_stock_consumed_again"] and not acted["government_ack_created"]
  print("PASS089 authorized epsilon-outside act retains checked accepted3/open discrepancy/original source; two receipts each exact replay/photos3/outbox1/quantity journal0, old result survives equipment deactivation",flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)",a=sender,b=receiver);conn.commit()
