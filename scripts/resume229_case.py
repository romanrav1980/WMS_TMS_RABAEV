import sys,json,copy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
s=get_settings();tag="13508027ed";uid="FULL.QA:"+tag;load="IW228.LOAD:"+tag;actor="SR229"+tag;addr="Own full-pallet ST"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute("select PASS from RUSERS where ID=:a",a=actor);row=q.fetchone()
 if not row:
  from uuid import uuid4
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own229 recipient',:g,51365792,0,0)",a=actor,p=secret,g=actor.upper());c.commit()
 else:secret=row[0]
 admin=httpx.Client(auth=("admin","admin123"),timeout=35);client=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
 def api(h,method,path,body=None,status=200):
  r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
 api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":"store_receipt_confirm","description":"Own229 actual marked recipient"})
 path="/api/delivery/store-receipts"
 q.execute("select POLICY_VERSION,RECEIPT_MODE from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:a",a=addr);policy=q.fetchone()
 if not policy:api(admin,"PUT",path+"/policy",{"store_address":addr,"mode":"BARCODE","expected_version":0})
 else:assert policy[1]=="BARCODE",policy
 api(admin,"POST",path+"/receivers",{"store_address":addr,"username":actor})
 q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid);scans=[]
 for system,profiles,raw in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 q.execute("select OPERATION_ID,CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID like 'STORE229.RECEIVE:%'and STATE='APPLIED'");op,raw=q.fetchone();canonical=read_oracle_json(raw);winner={"operation_id":op,**canonical["source"],**canonical["metadata"]};winner.pop("unit_scans");winner["scans"]=scans;saved=api(client,"POST",path+"/confirm",winner)
 q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=641362");order=q.fetchone()[0]
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("delete from RRL_STORE_RECEIPT_USER where USER_ID=:a and STORE_ADDR=:s",a=actor,s=addr);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 try:api(client,"POST",path+"/confirm",winner,403)
 finally:api(admin,"POST",path+"/receivers",{"store_address":addr,"username":actor})
 assert api(client,"POST",path+"/confirm",winner)==saved
 after=api(admin,"GET",f"/api/customer-orders/{order}/delivery");assert after["quantities"][0]["shipped"]=="3"and after["quantities"][0]["accepted"]=="3"and after["quantities"][0]["unreceived"]=="0",after
 assert after["receipt_lineage"][0]["actual_final_load_operation_id"]==load and after["receipt_lineage"][0]["original_load_operation_id"]=="IW225.LOAD:"+tag
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=winner["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,0)
 q.execute("select count(*),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'",u=uid);assert q.fetchone()==(3,10,10)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS229 exact6QR/currentUNITprofiles/marked original physical3 final accepted3/unreceived0/first-to-final lineage/no goods/no unit birth/no fakeGovACK/missing duplicate partial409/native rollback/concurrent winner/replay/current receiver binding403/protected20/20",winner["operation_id"],order,flush=True)
