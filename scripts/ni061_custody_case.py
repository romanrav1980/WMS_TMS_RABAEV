import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QIC"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();receipt="INTERWARE.RECEIVE:349bc1ff57";load="SINGLE.FULL.LOAD:9b15cf997d"
 q.execute("select TT_ID,ROOT_UID,STATUS,DEPARTURE_OPERATION_ID,DEPARTED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=load);original=q.fetchone()
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own target custody actor',:grp,9104,0,0)",id=actor,secret=secret,grp=group);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own target custody actor"})
 for right in ["interwarehouse_receive","transport_dispatch_view"]:api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own target custody actor"})
 try:
  p="/api/inventory/interwarehouse/release-custody";body={"operation_id":"INTERWARE.CUSTODY:"+tag,"receipt_operation_id":receipt}
  q.execute("update RUSERS set WARE_ID=2378876 where ID=:id",id=actor);c.commit()
  api(user,p,body,403)
  q.execute("update RUSERS set WARE_ID=9104 where ID=:id",id=actor);c.commit()
  result=api(user,p,body);assert result["status"]=="FIRST_LEG_CUSTODY_RELEASED" and not result["stock_changed"] and result["original_departure_retained"] and not result["customer_delivery_confirmed"]
  assert api(user,p,body)==result
  api(user,p,{**body,"receipt_operation_id":"FOREIGN"},409)
  api(user,p,{**body,"operation_id":"INTERWARE.CUSTODY.SECOND:"+tag},409)
  q.execute("select TT_ID,ROOT_UID,STATUS,DEPARTURE_OPERATION_ID,DEPARTED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=load);assert q.fetchone()==original
  q.execute("select count(*)from RRL_TT_HU_LOAD_FACT f join RRL_INTERWARE_CUSTODY_PROOF p on p.OPERATION_ID=f.CUSTODY_RELEASE_OPERATION_ID join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=p.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNLOAD u on u.OPERATION_ID=r.UNLOAD_OPERATION_ID where f.LOAD_OPERATION_ID=:op and f.CUSTODY_RELEASED_AT=u.CREATED_AT",op=load);assert q.fetchone()==(1,)
  q.execute("select count(*)from RRL_TT_HU_LOAD_FACT where ROOT_UID=:lot_id and STATUS in('LOADED','DEPARTED')and CUSTODY_RELEASED_AT is null",lot_id=original[1]);assert q.fetchone()==(0,)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=original[1]);assert q.fetchone()==(3,0)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and ACTIVE_FLAG=1",op=load);assert q.fetchone()==(1,)
  try:q.execute("update RRL_TT_HU_LOAD_FACT set CUSTODY_RELEASED_AT=null where LOAD_OPERATION_ID=:op",op=load)
  except oracledb.DatabaseError as exc:assert getattr(exc.args[0],"code",0)==20863;c.rollback()
  else:raise AssertionError("Direct custody history edit allowed")
  print("PASS121 current target actor/foreign403/root custody proof/actual unload timestamp/source DEPARTED and original ST retained/activeUID0/P3H0/event0/replay/conflict/second/direct edit denied; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_INTERWARE_CUSTODY%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""");print("SQL milliseconds/executions",q.fetchall())
