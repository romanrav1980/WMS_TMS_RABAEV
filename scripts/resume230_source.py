exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
from datetime import datetime,timedelta,timezone
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select LOAD_OPERATION_ID,ROOT_UID,WARE_ID,TT_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID like 'IW225.LOAD:%'and ROOT_UID!='FULL.QA:13508027ed' order by TT_ID desc fetch first 1 row only");load,uid,ware,trip=q.fetchone();tag=uid.split(':')[1]
 q.execute("select SBORKA_PALLET_ID from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:p",p=load);st=q.fetchone()[0]
 q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:p",p=st);order=q.fetchone()[0]
 q.execute("select ID from RRL_TRANSPORT_TASK where DOCK=:d",d="QO225"+tag);target_trip=q.fetchone()[0]
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET=:u",u=uid);article=q.fetchone()[0]
 q.execute("select VEHICLE_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load);vehicle=q.fetchone()[0]
 now=datetime.now(timezone.utc);body={"operation_id":"IW225.PLAN:"+tag,"source_load_operation_id":load,"target_warehouse_id":ware+50000000,"target_trip_id":target_trip,"inbound_dock":"QI225"+tag,"arrival_due":(now+timedelta(hours=1)).isoformat(),"ready_due":(now+timedelta(hours=2)).isoformat(),"reason":"Own230 exact marked source original committed load retained","decision_reference":"IW230:"+tag}
 with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
  r=h.post("http://127.0.0.1:8088/api/inventory/interwarehouse/plan",json=body);assert r.status_code==200,(r.status_code,r.text[:2200]);plan=r.json();assert plan["physical_unit_count"]==3
 print(json.dumps({"tag":tag,"uid":uid,"article":article,"source_ware":ware,"target_ware":ware+50000000,"source_st":st,"source_trip":trip,"target_trip":target_trip,"plan":body["operation_id"],"load":load,"inbound":"QI225"+tag,"outbound":"QO225"+tag,"vehicle":vehicle,"order":order},ensure_ascii=True))
