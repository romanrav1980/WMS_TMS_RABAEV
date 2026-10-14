import json,sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();a=json.loads(Path("tmp/context241a.json").read_text(encoding="utf-8"));b=json.loads(Path("tmp/context241b.json").read_text(encoding="utf-8"));assert a["target_ware"]==b["target_ware"]
h=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088";tag=a["tag"];plate="QC241"+tag;dock="QC241"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,"15",200,2,0,None]));c.commit()
 meta("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
 q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=int(q.fetchone()[0])
 meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock,ware=a["target_ware"])
 meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)select :id,:plate,'15','Спланирован',SHIPMENT_DATE,VODITEL_ID,:dock,0 from RRL_TRANSPORT_TASK where ID=:old",id=trip,plate=plate,dock=dock,old=a["target_trip"])
 for ctx in [a,b]:
  body={"operation_id":"IW241.DEFER:"+ctx["tag"],"plan_operation_id":ctx["plan"],"decision_kind":"DEFER","expected_revision":0,"expected_arrival":(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),"target_trip_id":trip,"ready_due":(datetime.now(timezone.utc)+timedelta(hours=3)).isoformat(),"reason":"Own two independent source pallets consolidate on existing target trip","decision_reference":"IW241:"+tag}
  r=h.post(base+"/api/inventory/interwarehouse/decisions",json=body);assert r.status_code==200,(r.status_code,r.text)
  ctx.update(original_target_trip=ctx["target_trip"],target_trip=trip,original_outbound=ctx["outbound"],outbound=dock,target_vehicle_number=plate)
 r=h.get(base+f"/api/inventory/interwarehouse/trips/{trip}/incoming");assert r.status_code==200,r.text
 board=r.json();assert board["expected_deliveries"]==2 and board["ready_deliveries"]==0 and len(board["expected_quantities"])==2 and not board["departure_authorized"],board
 assert {x["source_ware_id"]for x in board["plans"]}=={a["source_ware"],b["source_ware"]}
 q.execute("select WEIGHT,PALLET_COUNT from RRL_TR_VEHICLE where ID=:id",id=vehicle);print("OWN_VEHICLE_CAPACITY",q.fetchone())
 print("CTX241A:"+json.dumps(a));print("CTX241B:"+json.dumps(b));print("BOARD241",json.dumps(board))
