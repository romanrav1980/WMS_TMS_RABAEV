"""Synthetic gateway packet: real API/Oracle archive, not hardware acceptance."""
import json,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];sender="QSCALE"+tag;group="QC"+tag.upper();password=uuid4().hex;device="DEV.SCALE:"+tag
admin=httpx.Client(auth=("admin","admin123"),timeout=25);gateway=httpx.Client(auth=(sender,password),timeout=25)
base="/api/delivery/store-scales";addr="STORE.QA:bea258a7dd";load="FULL.HU.SHIP:bea258a7dd"
def stamp(value):return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
def call(client,method,path,body=None,status=200):
 r=client.request(method,"http://127.0.0.1:8088"+path,json=body)
 assert r.status_code==status,(r.status_code,r.text[:1300]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN) values(:id,:password,'Own scale gateway',:group_id,0,0)",id=sender,password=password,group_id=group);conn.commit()
 try:
  call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own synthetic scale gateway"})
  call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"store_scale_ingest","description":"Own gateway packet"})
  now=datetime.now(timezone.utc);policy={"store_address":addr,"sender_id":sender,"expected_version":0,"active":True,"capacity_kg":"100","resolution_kg":"0.01","calibration_ref":"DEV.SYNTHETIC:"+tag,"calibrated_until":stamp(now+timedelta(days=1))}
  refusal=call(admin,"PUT",base+"/devices/"+device,{**policy,"sender_id":"admin"},status=409)
  assert refusal["detail"]["code"]=="SCALE_DEDICATED_SENDER_REQUIRED"
  configured=call(admin,"PUT",base+"/devices/"+device,policy);assert configured["device_policy_version"]==1
  now=datetime.now(timezone.utc)
  packet={"device_id":device,"capture_id":"READ:"+tag,"load_operation_id":load,"store_address":addr,
   "device_policy_version":1,"calibration_ref":policy["calibration_ref"],"unit":"KG","basis":"GROSS","preset_tare_kg":"0",
   "zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=60)),"measured_at":stamp(now),
   "samples":[{"offset_ms":i*500,"gross_weight_kg":"10"} for i in range(5)]}
  for suffix,change,rule in (
   ("UNSTABLE",{"samples":[*packet["samples"][:-1],{"offset_ms":2000,"gross_weight_kg":"10.03"}]},"SCALE_STABLE_WINDOW_REQUIRED"),
   ("ZERO",{"zero_confirmed":False},"SCALE_ZERO_CONFIRMATION_REQUIRED"),
   ("OLD",{"measured_at":stamp(now-timedelta(seconds=40))},"SCALE_FRESH_ZERO_AND_MEASUREMENT_REQUIRED"),
   ("CAPACITY",{"samples":[{**sample,"gross_weight_kg":"101"} for sample in packet["samples"]]},"SCALE_SAMPLE_ORDER_OR_CAPACITY_INVALID"),
   ("VERSION",{"device_policy_version":2},"SCALE_DEVICE_POLICY_CHANGED")):
   rejected=call(gateway,"POST",base+"/captures",{**packet,**change,"capture_id":"BAD."+suffix+":"+tag},status=409)
   assert rule in rejected["detail"]["message"],rejected
  capture=call(gateway,"POST",base+"/captures",packet);assert capture["gross_weight_kg"]=="10" and not capture["receipt_confirmed"]
  assert call(gateway,"POST",base+"/captures",packet)==capture
  conflict=call(gateway,"POST",base+"/captures",{**packet,"zero_check_kg":"0.01"},status=409)
  assert "SCALE_CAPTURE_PAYLOAD_CONFLICT" in conflict["detail"]["message"]
  assert call(admin,"GET",base+"/captures/"+capture["capture_key"])==capture
  call(admin,"POST",base+"/captures",{**packet,"capture_id":"WRONG.SENDER:"+tag},status=403)
  call(gateway,"GET",base+"/captures/"+capture["capture_key"],status=403)
  call(gateway,"POST",base+"/captures",{**packet,"zero_confirmed":None,"capture_id":"NULL:"+tag},status=422)
  oversize=gateway.post("http://127.0.0.1:8088"+base+"/captures",content=b"x"*32001,headers={"Content-Type":"application/json"});assert oversize.status_code==413
  policy.update(expected_version=1,active=False)
  call(admin,"PUT",base+"/devices/"+device,policy)
  assert call(gateway,"POST",base+"/captures",packet)==capture
  rejected=call(gateway,"POST",base+"/captures",{**packet,"device_policy_version":2,"capture_id":"INACTIVE:"+tag},status=409)
  assert "SCALE_INACTIVE_OR_CALIBRATION_EXPIRED" in rejected["detail"]["message"]
  q.execute("select dbms_lob.substr(SOURCE_JSON,4000,1),SOURCE_SHA256,RESULT_JSON from RRL_STORE_SCALE_CAPTURE where CAPTURE_KEY=:key",key=capture["capture_key"])
  raw,sha,result=q.fetchone();raw=raw.read() if hasattr(raw,"read") else raw
  import hashlib
  assert hashlib.sha256(raw.encode()).hexdigest().upper()==sha
  assert json.loads(raw)==packet
  try:q.execute("delete RRL_STORE_SCALE_CAPTURE where CAPTURE_KEY=:key",key=capture["capture_key"]);conn.commit();raise AssertionError("Original capture deleted")
  except oracledb.DatabaseError as exc:conn.rollback();assert "SCALE_ORIGINAL_CAPTURE_IMMUTABLE" in str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='FULL.QA:bea258a7dd' and REMAIN>0");assert q.fetchall()==[]
  print("PASS087 synthetic authenticated gateway actual API original/hash/stable10KG/replay/conflict/reading/zero/stale/unstable/capacity/version/inactive/foreign sender/permission/null/oversize/append-only; no receipt or P/H effect",flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=sender);conn.commit()
