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
 dossier=api(client,"GET",path+receipt);assert len(dossier["units"])==2
 keys=[u["key"]for u in dossier["units"]]
 q.execute("select PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:p and UNIT_DISPOSITION='MISSING'",p=receipt);missing=q.fetchone()[0]
 body={"operation_id":"RET231.APP:"+tag,"line_no":1,"quantity":"1","disposition":"SUPPLIER","reason":"Own231 exact accepted physical unit","decision_reference":"RET231:"+tag,"unit_keys":[keys[0]]}
 bad=dict(body,operation_id="RET231.MISSING:"+tag,unit_keys=[missing]);api(client,"POST",path+receipt+"/approve",bad,409)
 bad=dict(body,operation_id="RET231.DUP:"+tag,unit_keys=[keys[0],keys[0]]);api(client,"POST",path+receipt+"/approve",bad,409)
 bad=dict(body,operation_id="RET231.QTY:"+tag,quantity="2");api(client,"POST",path+receipt+"/approve",bad,409)
 metadata={k:v for k,v in body.items()if k not in("operation_id","line_no")};metadata["complete_good_box"]=False
 command={"contract_version":2,"operation_id":"RET231.ROLLBACK:"+tag,"command_type":"STORE_RETURN_APPROVE","actor":actor,"source":{"receipt_operation_id":receipt,"line_no":1},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),actor,out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select count(*)from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=:p",p=command["operation_id"]);assert q.fetchone()[0]==1
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 def approve(i):
  value=dict(body,operation_id=body["operation_id"]+str(i))
  with httpx.Client(auth=(actor,secret),timeout=35)as h:return h.post(base+path+receipt+"/approve",json=value),value
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(approve,[0,1]))
 assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:3000])for r,b in results]
 saved,winner=next((r.json(),b)for r,b in results if r.status_code==200);assert saved["physical_unit_count"]==1 and not saved["warehouse_stock_changed"]
 assert api(client,"POST",path+receipt+"/approve",winner)==saved
 after=api(client,"GET",path+receipt);assert len(after["units"])==1 and after["units"][0]["key"]==keys[1]
 second=dict(body,operation_id="RET231.DISPOSAL:"+tag,unit_keys=[keys[1]],disposition="DISPOSAL",reason="Own231 second accepted unit warehouse inspection/disposal path")
 second_result=api(client,"POST",path+receipt+"/approve",second);assert second_result["physical_unit_count"]==1
 # Legacy229 full marked acceptance has no230 child facts: original frozen full proof supplies eligible units.
 legacy="STORE229.RECEIVE:13508027ed0";old=api(client,"GET",path+legacy);assert len(old["units"])==3
 legacy_body=dict(body,operation_id="RET231.LEGACY:13508027ed",unit_keys=[old["units"][0]["key"]],disposition="DISPOSAL")
 old_result=api(client,"POST",path+legacy+"/approve",legacy_body);assert old_result["physical_unit_count"]==1
 q.execute("update RUSERS set DELETED=1 where ID=:a",a=actor);c.commit()
 try:api(client,"POST",path+receipt+"/approve",winner,403)
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
 print("PASS231 current230accepted-only exact units1SUPPLIER/1DISPOSAL/legacy229full frozen proof1/no duplicate or missing-unit approval/native rollback/concurrent same-unit one winner/replay/inactive403/appendonly/no goods or GovACK/protected20/20",winner["operation_id"],second["operation_id"],legacy_body["operation_id"],flush=True)
