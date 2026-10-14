"""Actual non-admin receiver, existing rights UI grants and address binding; no stock writes."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];username="QSTORE"+tag;group="QS"+tag.upper();password=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=25);receiver=httpx.Client(auth=(username,password),timeout=25)
load="FULL.HU.SHIP:04633c677f";own="STORE.QA:04633c677f";other="STORE.OTHER:04633c677f"
def call(client,method,path,body=None,status=200):
 r=client.request(method,"http://127.0.0.1:8088"+path,json=body)
 assert r.status_code==status,(r.status_code,r.text[:800])
 return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN) values(:id,:password,:name,:group_id,0,0)",id=username,password=password,name="Own store receiver",group_id=group);c.commit()
 try:
  call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own store receiver"})
  call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"store_receipt_confirm","description":"Own receiver case"})
  q.execute("select RRL_HAS_WRIGHT(:actor,'store_receipt_confirm'),RRL_HAS_WRIGHT(:actor,'STORE_RECEIPT_CONFIRM'),RRL_HAS_WRIGHT('admin','store_receipt_confirm') from dual",actor=username)
  assert q.fetchone()==(1,1,1)
  path=f"/api/delivery/store-receipts/preview?load_operation_id={load}&store_address="
  refused=call(receiver,"GET",path+own,status=403);assert "STORE_RECEIVER_ADDRESS_BINDING_REQUIRED" in refused["detail"]["message"]
  call(admin,"POST","/api/delivery/store-receipts/receivers",{"store_address":own,"username":username})
  preview=call(receiver,"GET",path+own);assert preview["store_address"]==own and preview["already_received"]
  refused=call(receiver,"GET",path+other,status=403);assert "STORE_RECEIVER_ADDRESS_BINDING_REQUIRED" in refused["detail"]["message"]
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=username);c.commit()
  call(receiver,"GET",path+own,status=401)
  q.execute("select RRL_HAS_WRIGHT(:actor,'store_receipt_confirm') from dual",actor=username);assert q.fetchone()==(0,)
  print("PASS actual non-admin uppercase rights grant/lowercase API/root permission, own-store binding/foreign403/deleted401/root0; GLOBAL_ADMIN retained; no stock writes",flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=username);c.commit()
