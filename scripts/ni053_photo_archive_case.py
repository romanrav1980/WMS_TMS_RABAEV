"""Actual image decoding/archive/retrieval source proof, no new stock setup."""
import sys,json
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from PIL import Image
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();client=httpx.Client(auth=("admin","admin123"),timeout=35)
load="FULL.HU.SHIP:04633c677f";store="STORE.QA:04633c677f";other="STORE.OTHER:04633c677f"
def image(color,fmt):
 stream=BytesIO();Image.new("RGB",(320,240),color).save(stream,format=fmt);return stream.getvalue()
def upload(view,contents,mime="image/png",address=store,status=200):
 r=client.post("http://127.0.0.1:8088/api/delivery/store-photos/upload",
  params={"load_operation_id":load,"store_address":address,"view":view},content=contents,headers={"Content-Type":mime})
 assert r.status_code==status,(r.status_code,r.text[:1200])
 return r
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();ids=[]
 for view,color,fmt,mime in (("FRONT","red","PNG","image/png"),("LEFT","green","JPEG","image/jpeg"),("RIGHT","blue","PNG","image/png")):
  contents=image(color,fmt);r=upload(view,contents,mime);data=r.json();ids.append(data["photo_id"])
  assert data["sha256"]==sha256(contents).hexdigest().upper() and data["byte_count"]==len(contents)
  assert upload(view,contents,mime).json()==data
  recovered=client.get("http://127.0.0.1:8088/api/delivery/store-photos/"+data["photo_id"]+"/content")
  assert recovered.status_code==200 and recovered.content==contents
  assert recovered.headers["etag"].strip('"')==data["sha256"]
  call_id=int(r.headers["X-WMS-API-Call-Id"])
  q.execute("select REPLAYABLE,REQUEST_BODY,REQUEST_BODY_SHA256 from RRL_API_CALL_LOG where API_CALL_ID=:id",id=call_id)
  replayable,log_body,digest=q.fetchone();log_body=log_body.read() if hasattr(log_body,"read") else log_body
  assert replayable==0 and json.loads(log_body)["binary"] and digest==sha256(contents).hexdigest()
 upload("BACK",b"invalid image",status=422)
 upload("BACK",image("white","PNG"),"image/jpeg",status=422)
 upload("BACK",image("white","PNG"),address=other,status=409)
 upload("BACK",b"x"*(4*1024*1024+1),status=413)
 listing=client.get("http://127.0.0.1:8088/api/delivery/store-photos/list",params={"load_operation_id":load,"store_address":store})
 assert listing.status_code==200 and {row["photo_id"] for row in listing.json()}>=set(ids)
 try:q.execute("delete from RRL_STORE_RECEIPT_PHOTO where PHOTO_ID=:id",id=ids[0]);c.commit();raise AssertionError("Photo association deleted")
 except oracledb.DatabaseError as exc:c.rollback();assert "PHOTO_ORIGINAL_ASSOCIATION_IMMUTABLE" in str(exc),str(exc)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0) from RRL_REMAINS where UID_POLETA like 'FULL.QA:04633c677f%'");assert q.fetchone()==(0,0)
 print("PASS actual PNG/JPEG/three views/original byte+hash recovery/exact upload replay/foreign source and bad MIME/image/4MiB refusals; audit hash metadata/nonreplayable, immutable source, P/H0",flush=True)
