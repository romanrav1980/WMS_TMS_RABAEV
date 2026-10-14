import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QFC"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();ware=2378876;p="/api/finance/logistics-costs"
 q.execute("select REASON_TEXT,DECISION_REFERENCE from RRL_LOGISTICS_RATE_HISTORY h join RRL_LOGISTICS_RATE_HEAD r on r.RATE_KEY=h.RATE_KEY where r.WARE_ID=:ware and r.CURRENCY='GEL' and h.VERSION_NO=1",ware=ware);reason,reference=q.fetchone()
 body={"warehouse_id":ware,"currency":"GEL","rate":"2.50","effective_from":"2026-01-01","expected_version":0,"reason":reason,"decision_reference":reference}
 retried=api(admin,p+"/rates",body);assert retried["version"]==1
 api(admin,p+"/rates",{**body,"rate":"2.51"},409)
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own finance scope observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own finance scope"})
 for right in ["transport_dispatch_view","calc_tt_price","create_tt_price"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own finance scope"})
 try:
  assert api(user,p+f"/warehouses/{ware}/rates")[0]["version_no"]==2
  api(user,p+"/warehouses/9104/rates",status=403)
  api(user,p+"/calculate",{"operation_id":"COST.FOREIGN:"+tag,"trip_id":33514,"warehouse_id":9104,"currency":"GEL"},403)
  result=api(user,p+"/trips/33514");assert result["lines"][0]["version_no"]==1
  print("PASS111 original norm retry after future version returns originalv1; changed original rate conflicts, bound non-admin sees own and foreign warehouse denied, current charge frozenv1")
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
