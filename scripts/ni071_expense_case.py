import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QEX"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body=None,status=200):
 r=client.request("POST" if body else "GET",base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1700]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();ware=2378876;trip=33514;p="/api/finance/logistics-expenses"
 q.execute("select VEHICLE_ID from RRL_TT_HU_LOAD_FACT where TT_ID=:trip",trip=trip);vehicle=int(q.fetchone()[0])
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own transport expense observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own extra expense"})
 for right in ["transport_dispatch_view","edit_bill_tt","calc_tt_price","create_tt_price"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own extra expense fixture"})
 try:
  q.execute("select count(*)from RRL_EVENTS");goods=q.fetchone()[0]
  article={"code":"EX.QA:"+tag.upper(),"name":"Own exceptional transport expense","scope":"BOTH","included_in_rate":False,"active":True,"expected_version":0}
  api(admin,p+"/articles",article);assert api(admin,p+"/articles",article)["version"]==1
  api(admin,p+"/articles",{**article,"code":"WAREHOUSE_PICKING"},409)
  included={**article,"code":"EX.COMMON:"+tag.upper(),"included_in_rate":True};api(admin,p+"/articles",included)
  report={"operation_id":"EX.REPORT:"+tag,"warehouse_id":ware,"article_code":article["code"],"object_kind":"TRIP","object_id":trip,"amount":"10.01","currency":"GEL","expense_date":"2026-10-10","document_reference":"EXPENSE:"+tag,"reason":"Own exceptional documented expense"}
  api(user,p+"/report",{**report,"operation_id":"EX.BAD.COMMON:"+tag,"article_code":included["code"]},409)
  saved=api(user,p+"/report",report);assert api(user,p+"/report",report)==saved
  api(user,p+"/report",{**report,"amount":"10.02"},409)
  decision={"operation_id":"EX.LOGIST:"+tag,"expense_operation_id":report["operation_id"],"phase":"LOGIST","outcome":"APPROVE","distribution_basis":"WEIGHT","decision_reference":"LOGIST:"+tag,"reason":"Own confirmed source expense and weight distribution"}
  logistic=api(user,p+"/decide",decision);assert logistic["status"]=="LOGIST_APPROVED" and api(user,p+"/decide",decision)==logistic
  financial={**decision,"operation_id":"EX.FINANCE:"+tag,"phase":"FINANCE","decision_reference":"FIN:"+tag}
  api(user,p+"/decide",financial,403)
  confirmed=api(admin,p+"/decide",financial);assert confirmed["status"]=="APPROVED_PENDING_ALLOCATION" and api(admin,p+"/decide",financial)==confirmed
  vehicle_report={**report,"operation_id":"EX.VEH.REPORT:"+tag,"object_kind":"VEHICLE","object_id":vehicle,"amount":"4.00"}
  api(user,p+"/report",vehicle_report)
  vehicle_decision={**decision,"operation_id":"EX.VEH.BAD:"+tag,"expense_operation_id":vehicle_report["operation_id"]}
  api(user,p+"/decide",vehicle_decision,409)
  vehicle_decision.update(operation_id="EX.VEH.LOGIST:"+tag,distribution_basis="NONE");api(user,p+"/decide",vehicle_decision)
  vehicle_fin={**vehicle_decision,"operation_id":"EX.VEH.FINANCE:"+tag,"phase":"FINANCE"}
  assert api(admin,p+"/decide",vehicle_fin)["status"]=="APPROVED_VEHICLE_ONLY"
  q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==goods
  print("PASS112 extra catalog/included rate refused, trip10.01 GEL/report replay/conflict/logist weight/independent finance403->approved pending allocation; vehicle4.00 weight denied/NONE approved vehicle only/no goods; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%RRL_LOGISTICS_EXP%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
