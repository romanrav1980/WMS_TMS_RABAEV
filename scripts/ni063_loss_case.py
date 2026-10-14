import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];ware=20000000+int(tag[:6],16);actor="QTL"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def call(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1700]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("insert into RRL_WARES(ID,NAME,PREFIX)values(:ware,:name,:prefix)",ware=ware,name="Own tare loss "+tag,prefix="Z"+tag[:2]);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own warehouse loss observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 call(admin,"/api/admin/rights/groups",{"id":group,"name":"Own warehouse tare loss"})
 for right in ["tare_loss_report","tare_view","tare_writeoff"]:
  call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own loss scenario"})
 p="/api/inventory/tare"
 call(admin,p+"/count",{"operation_id":"LOSS.COUNT:"+tag,"owner_ware_id":ware,"pallet_type_id":3,"condition":"GOOD","observed_quantity":"3","expected_version":0,"reason":"Own physical count declaration","decision_reference":"COUNT:"+tag})
 def current():return next(x for x in call(admin,p+f"/warehouses/{ware}/availability") if x["pallet_type_id"]==3)
 row=current()
 report={"operation_id":"LOSS.REPORT:"+tag,"owner_ware_id":ware,"pallet_type_id":3,"condition":"GOOD","quantity":"1","expected_version":row["balance_version"],"reason":"Own missing observed unit","decision_reference":"LOSS:"+tag}
 result=call(user,p+"/loss-report",report);assert result["status"]=="REPORTED"
 assert call(user,p+"/loss-report",report)==result
 row=current();assert(row["physical_quantity"],row["loss_pending_quantity"],row["available_quantity"])==("3","1","2")
 call(admin,p+"/count",{"operation_id":"LOSS.BAD.COUNT:"+tag,"owner_ware_id":ware,"pallet_type_id":3,"condition":"GOOD","observed_quantity":"0","expected_version":row["balance_version"],"reason":"Cannot hide claim","decision_reference":"BAD:"+tag},409)
 call(admin,p+"/damage",{"operation_id":"LOSS.BAD.DAMAGE:"+tag,"owner_ware_id":ware,"pallet_type_id":3,"custodian_kind":"WAREHOUSE","custodian_id":str(ware),"quantity":"3","reason":"Cannot spend missing asset","decision_reference":"BAD:"+tag},409)
 decision={"operation_id":"LOSS.WRITE:"+tag,"claim_operation_id":report["operation_id"],"outcome":"WRITE_OFF","reason":"Independent confirmed missing unit","decision_reference":"DECIDE:"+tag}
 call(user,p+"/loss-decide",decision,403)
 posted=call(admin,p+"/loss-decide",decision);assert call(admin,p+"/loss-decide",decision)==posted
 row=current();assert(row["physical_quantity"],row["loss_pending_quantity"],row["available_quantity"])==("2","0","2")
 report2={**report,"operation_id":"LOSS.REPORT2:"+tag,"expected_version":row["balance_version"]}
 call(user,p+"/loss-report",report2)
 reject={**decision,"operation_id":"LOSS.REJECT:"+tag,"claim_operation_id":report2["operation_id"],"outcome":"REJECT","reason":"Own unit located, cancel suspicion"}
 call(admin,p+"/loss-decide",reject)
 row=current();assert(row["physical_quantity"],row["loss_pending_quantity"],row["available_quantity"])==("2","0","2")
 for op in [report["operation_id"],decision["operation_id"],report2["operation_id"],reject["operation_id"]]:
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
 q.execute("select count(*) from RRL_TARE_LOSS_DECISION where CLAIM_OPERATION_ID=:op",op=report["operation_id"]);assert q.fetchone()==(1,)
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_TARE_LOSS_%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("PASS105 own non-admin report physical3/free2, COUNT/DAMAGE refused, same actor403, independent loss writeoff physical2/free2/replay, second rejected claim free restored, no goods events")
 print("SQL milliseconds/executions",q.fetchall())
 call(admin,p+"/count",{"operation_id":"LOSS.END.COUNT:"+tag,"owner_ware_id":ware,"pallet_type_id":3,"condition":"GOOD","observed_quantity":"0","expected_version":row["balance_version"],"reason":"End own software fixture only","decision_reference":"END:"+tag})
 q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
