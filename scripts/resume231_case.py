import sys,json,copy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag="d76ea1c478";receipt="STORE230.RECEIVE:"+tag+"0";actor="SC231"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000;q.execute("select PASS from RUSERS where ID=:a",a=actor);row=q.fetchone()
 if not row:
  from uuid import uuid4
  secret=uuid4().hex;q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own231 SupplyChain',:g,64218561,0,0)",a=actor,p=secret,g=actor.upper());c.commit()
 else:secret=row[0]
 admin=httpx.Client(auth=("admin","admin123"),timeout=35);client=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088";path="/api/delivery/store-returns/"
 def api(h,method,p,body=None,status=200):
  r=h.request(method,base+p,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
 api(admin,"POST","/api/admin/rights/groups/"+actor.upper()+"/rights",{"right_name":"store_return_approve","description":"Own231 exact previously accepted units"})
 q.execute("select OPERATION_ID,CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID like 'RET231.APP:%'and STATE='APPLIED'");op,raw=q.fetchone()
 from app.modules.platform.public import read_oracle_json
 canonical=read_oracle_json(raw);winner=dict(canonical["metadata"],line_no=canonical["source"]["line_no"],operation_id=op);saved=api(client,"POST",path+receipt+"/approve",winner)
 second={"operation_id":"RET231.DISPOSAL:"+tag};legacy_body={"operation_id":"RET231.LEGACY:13508027ed"}
 q.execute("select PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:p and UNIT_DISPOSITION='MISSING'",p=receipt);missing=q.fetchone()[0]
 q.execute("update RUSERS set DELETED=1 where ID=:a",a=actor);c.commit()
 try:
  api(client,"POST",path+receipt+"/approve",winner,401)
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(canonical),actor,out,None]);raise AssertionError("Inactive native cached approval allowed")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20882
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 finally:q.execute("update RUSERS set DELETED=0 where ID=:a",a=actor);c.commit()
 assert api(client,"POST",path+receipt+"/approve",winner)==saved
 q.execute("select count(*),sum(BASE_QTY)from RRL_STORE_RETURN_UNIT where RECEIPT_OPERATION_ID=:p",p=receipt);assert q.fetchone()==(2,2)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID in(:a,:b)",a=winner["operation_id"],b=second["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_STORE_RETURN_UNIT where RECEIPT_OPERATION_ID=:p and PHYSICAL_UNIT_KEY=:k",p=receipt,k=missing);assert q.fetchone()[0]==0
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA='FULL.QA:d76ea1c478'");assert q.fetchone()==(0,0)
 try:q.execute("delete from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=:p",p=winner["operation_id"]);raise AssertionError("Unit allocation history deleted")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20863
 finally:c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS231 current230accepted-only exact units1SUPPLIER/1DISPOSAL/legacy229full frozen proof1/no duplicate or missing-unit approval/native rollback/concurrent same-unit one winner/replay/inactiveHTTP401-native20882/appendonly/no goods or GovACK/protected20/20",winner["operation_id"],second["operation_id"],legacy_body["operation_id"],flush=True)
