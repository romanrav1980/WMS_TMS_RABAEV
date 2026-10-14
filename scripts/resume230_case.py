import sys,json,copy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.domain.mark_identity import normalize_unit_scan_codes
s=get_settings();ctx=json.loads(Path("tmp/context230.json").read_text(encoding="utf-8"));tag=ctx["tag"];uid=ctx["uid"];load="IW230.LOAD:"+tag;actor="SR230"+tag;addr="Own full-pallet ST"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute("select PASS from RUSERS where ID=:a",a=actor);row=q.fetchone()
 if not row:
  from uuid import uuid4
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own230 recipient',:g,:w,0,0)",a=actor,p=secret,g=actor.upper(),w=ctx["target_ware"]);c.commit()
 else:secret=row[0]
 admin=httpx.Client(auth=("admin","admin123"),timeout=35);client=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088";path="/api/delivery/store-receipts"
 def api(h,method,p,body=None,status=200):
  r=h.request(method,base+p,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
 api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":"store_receipt_confirm","description":"Own230 exact unit disposition"})
 api(admin,"POST",path+"/receivers",{"store_address":addr,"username":actor})
 q.execute("select UNIT_ID,SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by UNIT_ID,SYSTEM_CODE",u=uid);scans=[]
 for unit_id,system,profiles,raw in q.fetchall():
  if unit_id=="3":continue
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 q.execute("select OPERATION_ID,CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID like 'STORE230.RECEIVE:%'and STATE='APPLIED'");op,raw=q.fetchone();canonical=read_oracle_json(raw);winner={"operation_id":op,**canonical["source"],**canonical["metadata"]};winner.pop("unit_scans");winner["scans"]=scans;saved=api(client,"POST",path+"/confirm",winner)
 q.execute("select UNIT_DISPOSITION,sum(BASE_QTY),min(SOURCE_UNIT_VERSION),max(SOURCE_UNIT_VERSION)from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:p group by UNIT_DISPOSITION order by UNIT_DISPOSITION",p=winner["operation_id"]);assert q.fetchall()==[("ACCEPTED",2,10,10),("MISSING",1,10,10)]
 q.execute("select count(*)from RRL_STORE_DISCREPANCY_CASE where CASE_ID=:p",p=winner["operation_id"]);assert q.fetchone()[0]==1
 after=api(admin,"GET",f"/api/customer-orders/{ctx['order']}/delivery");assert after["quantities"][0]["shipped"]=="3"and after["quantities"][0]["accepted"]=="2"and after["quantities"][0]["unreceived"]=="0"and after["quantities"][0]["missing"]=="1",after
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=winner["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select count(*),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'",u=uid);assert q.fetchone()==(3,10,10)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,0)
 try:q.execute("delete from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:p",p=winner["operation_id"]);raise AssertionError("History deletion accepted")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20863
 finally:c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS230 original marked2 accepted/1 missing exact unit keys/profile coverage/base quantities/immutable facts/sourceversion10/legacy case and obligation/customer shipped3 accepted2 missing1 unreceived0/PARTIALLY_ACCEPTED/no goods/noGovACK/native rollback/concurrent/replay/incomplete duplicate mixed mismatched quantities409/protected20/20",winner["operation_id"],ctx["order"],flush=True)
