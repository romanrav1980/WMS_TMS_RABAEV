"""Own store damage and independent transport write-off; no goods effect."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088";p="/api/inventory/tare";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("""
 select d.ACCEPT_OPERATION_ID,d.STORE_ADDR,d.POLICY_VERSION,to_char(d.EFFECTIVE_DUE_AT,'YYYY-MM-DD HH24:MI:SS TZH:TZM'),a.ACCEPTED_BY,u.PASS,u.USER_GROUP
 from RRL_TARE_STORE_DEBT d join RRL_TARE_ACCEPT a on a.OPERATION_ID=d.ACCEPT_OPERATION_ID join RUSERS u on u.ID=a.ACCEPTED_BY
 where d.OWNER_WARE_ID=9104 and d.PALLET_TYPE_ID=3 and d.CONDITION_CODE='GOOD' and d.OUTSTANDING_QTY=2 and a.ACCEPTED_BY like 'QTS%'
 """);delivery,store,policy_version,due,user,password,group=q.fetchone();assert user.startswith("QTS")
 q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=user);c.commit()
 try:
  for right in ["tare_damage","tare_writeoff"]:
   call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own tare damage author role"})
  with httpx.Client(auth=(user,password),timeout=35) as shop:
   damage={"operation_id":"TARE.DAMAGE:"+tag,"owner_ware_id":9104,"pallet_type_id":3,"custodian_kind":"STORE","custodian_id":store,"delivery_accept_operation_id":delivery,"quantity":"2","reason":"Own two damaged trolleys inspected in store","decision_reference":"OBS:"+tag}
   result=call(shop,p+"/damage",damage);assert not result["total_tare_changed"] and not result["goods_stock_changed"]
   assert call(shop,p+"/damage",damage)==result
   debt=call(shop,p+"/warehouses/9104/store-debt");own=[r for r in debt if r["store_addr"]==store and r["pallet_type_id"]==3]
   assert len(own)==1 and own[0]["condition_code"]=="DAMAGED" and own[0]["outstanding_quantity"]=="2" and own[0]["policy_version"]==policy_version
   writeoff={"operation_id":"TARE.WRITEOFF:"+tag,"damage_operation_id":damage["operation_id"],"quantity":"1","reason":"Own transport department loss decision","decision_reference":"LOSS:"+tag}
   call(shop,p+"/writeoff",writeoff,403)
   call(admin,p+"/writeoff",{**writeoff,"operation_id":"TARE.WRITEOFF.EXCESS:"+tag,"quantity":"3"},409)
   decided=call(admin,p+"/writeoff",writeoff);assert decided["total_tare_changed"] and not decided["goods_stock_changed"]
   assert call(admin,p+"/writeoff",writeoff)==decided
  q.execute("select CUSTODIAN_KIND,CONDITION_CODE,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3")
  rows=q.fetchall();assert sum(r[2] for r in rows)==5 and next(r[2] for r in rows if r[:2]==('STORE','DAMAGED'))==1,rows
  q.execute("select OUTSTANDING_QTY,POLICY_VERSION,to_char(EFFECTIVE_DUE_AT,'YYYY-MM-DD HH24:MI:SS TZH:TZM') from RRL_TARE_STORE_DEBT where CLAIM_KEY=:damage",damage=damage["operation_id"]);assert q.fetchone()==(1,policy_version,due)
  for operation in [damage["operation_id"],writeoff["operation_id"]]:
   q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=operation);assert q.fetchone()==(0,)
   q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=operation);assert q.fetchone()==(1,)
  try:q.execute("delete from RRL_TARE_RESOLUTION where OPERATION_ID=:op",op=writeoff["operation_id"]);c.commit();raise AssertionError("Resolution deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert "TARE_RESOLUTION_HISTORY_IMMUTABLE" in str(exc)
  print("PASS100 actual store GOOD2->DAMAGED2 conserved6; independent writeoff1->total5/store damaged debt1, original policy/deadline preserved; replay/self-approval/excess denied/immutable/goods events0/outbox1 each",flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=user);c.commit()
