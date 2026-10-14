import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();p="/api/inventory/tare";base="http://127.0.0.1:8088";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def api(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("""select cl.OPERATION_ID,cl.OWNER_WARE_ID,cl.TRANSPORT_TASK_ID,b.CUSTODIAN_ID,v.NUM,tt.VODITEL_ID,cl.ACTOR,u.PASS,u.USER_GROUP
 from RRL_TARE_LOSS_CLAIM cl join RRL_TARE_BALANCE b on b.BALANCE_KEY=cl.BALANCE_KEY join RRL_TRANSPORT_TASK tt on tt.ID=cl.TRANSPORT_TASK_ID
 join RRL_TR_VEHICLE v on to_char(v.ID,'TM9')=b.CUSTODIAN_ID join RUSERS u on u.ID=cl.ACTOR
 where cl.OPERATION_ID like 'LOSS.VEH.REPORT:%' and not exists(select 1 from RRL_TARE_LOSS_DECISION d where d.CLAIM_OPERATION_ID=cl.OPERATION_ID)
 order by cl.CREATED_AT desc fetch first 1 row only""")
 op,ware,trip,vehicle,plate,driver,actor,secret,group=q.fetchone();tag=op.split(":")[-1]
 q.execute("update RUSERS set DELETED=0 where ID=:id",id=actor);c.commit()
 api(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"tare_offer","description":"Own current vehicle physical offer"})
 binding=api(admin,"GET",f"/api/transport/driver-bindings/{driver}");assert not binding["active"]
 enabled=api(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":True,"expected_version":binding["binding_version"]})
 try:
  user=httpx.Client(auth=(actor,secret),timeout=35)
  denied=api(user,"POST",p+"/offer",{"operation_id":"LOSS.VEH.BAD.OFFER:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"VEHICLE","from_id":vehicle,"to_kind":"WAREHOUSE","to_id":str(ware),"quantity":"1","scan_vehicle":plate},409)
  assert "TARE_SOURCE_HELD_FOR_ASSEMBLY" in denied["detail"]["message"]
  decision={"operation_id":"LOSS.VEH.REJECT:"+tag,"claim_operation_id":op,"outcome":"REJECT","reason":"Asset located, original custody unchanged","decision_reference":"FOUND:"+tag}
  result=api(admin,"POST",p+"/loss-decide",decision);assert api(admin,"POST",p+"/loss-decide",decision)==result
  q.execute("select QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=1 and CUSTODIAN_KIND='VEHICLE'",ware=ware);assert q.fetchone()==(1,)
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID in(:a,:b)",a=op,b=decision["operation_id"]);assert q.fetchone()==(0,)
  print("PASS106 original current driver claim blocked vehicle offer; independent reject restored vehicle1/no goods/replay")
 finally:
  api(admin,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":actor,"active":False,"expected_version":enabled["binding_version"]})
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%SOURCE_CLAIM_ID%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
