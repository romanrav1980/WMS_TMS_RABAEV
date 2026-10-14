import json,sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();ctx=json.loads(Path("tmp/context239.json").read_text(encoding="utf-8"));tag=ctx["tag"];base="http://127.0.0.1:8088"
h=httpx.Client(auth=("admin","admin123"),timeout=35)
def api(path,body,status=200):
 r=h.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=int(q.fetchone()[0]);dock="QX239"+tag
 meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:d,:w,0)",d=dock,w=ctx["target_ware"])
 meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)select :id,TRANSPORT,TRANSTYPE,'Спланирован',SHIPMENT_DATE,VODITEL_ID,:d,0 from RRL_TRANSPORT_TASK where ID=:old",id=trip,d=dock,old=ctx["target_trip"])
 old=ctx["target_trip"];old_dock=ctx["outbound"];now=datetime.now(timezone.utc)
 wait={"operation_id":"IW239.WAIT:"+tag,"plan_operation_id":ctx["plan"],"decision_kind":"WAIT","expected_revision":0,"expected_arrival":(now+timedelta(hours=1)).isoformat(),"reason":"Own dispatcher wait until original marked cargo arrives","decision_reference":"IW239:"+tag}
 def blocked(tt,op):
  result=api(f"/api/transport/loading/{tt}/depart",{"operation_id":op},409)
  assert "DEPART_EXPECTED_INTERWARE_CARGO_NOT_READY" in json.dumps(result),result
 blocked(old,"IW239.EARLY:"+tag)
 got=api("/api/inventory/interwarehouse/decisions",wait);assert got["revision"]==1 and got["target_trip_id"]==old and not got["stock_changed"],got
 assert api("/api/inventory/interwarehouse/decisions",wait)==got
 api("/api/inventory/interwarehouse/decisions",{**wait,"reason":"different"},409)
 defer={**wait,"operation_id":"IW239.DEFER:"+tag,"decision_kind":"DEFER","expected_revision":1,"target_trip_id":trip,"ready_due":(now+timedelta(hours=3)).isoformat(),"reason":"Own dispatcher defers original shipment to later existing trip"}
 # Native rollback leaves no metadata fact.
 payload={**defer,"operation_id":"IW239.ROLLBACK:"+tag,"actor":"admin"}
 for field in("expected_arrival","ready_due"):payload[field]=datetime.fromisoformat(payload[field]).astimezone(timezone.utc).isoformat(timespec="microseconds")
 out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:q.callproc("RRL_INTERWARE_ROUTING.record_decision",[json.dumps(payload,sort_keys=True,separators=(",",":")),"admin",out]);c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_INTERWARE_DECISION where OPERATION_ID=:op",op=payload["operation_id"]);assert q.fetchone()[0]==0
 def contender(i):
  body={**defer,"operation_id":"IW239.DEFER:"+tag+str(i)}
  r=h.post(base+"/api/inventory/interwarehouse/decisions",json=body);return body,r
 with ThreadPoolExecutor(2)as pool:results=list(pool.map(contender,[1,2]))
 assert sorted(r.status_code for _,r in results)==[200,409],[(r.status_code,r.text)for _,r in results]
 winner,response=next(x for x in results if x[1].status_code==200);got=response.json()
 assert got["revision"]==2 and got["previous_trip_id"]==old and got["target_trip_id"]==trip and not got["stock_changed"]
 assert api("/api/inventory/interwarehouse/decisions",winner)==got
 q.execute("select TARGET_TT_ID,OUTBOUND_DOCK from RRL_INTERWARE_PLAN where OPERATION_ID=:p",p=ctx["plan"]);assert q.fetchone()==(old,old_dock)
 q.execute("select RRL_INTERWARE_ROUTING.target_trip(:p),RRL_INTERWARE_ROUTING.outbound_dock(:p)from dual",p=ctx["plan"]);assert q.fetchone()==(trip,dock)
 blocked(trip,"IW239.DEFERRED_EARLY:"+tag)
 r=h.get(base+f"/api/inventory/interwarehouse/warehouses/{ctx['target_ware']}");assert r.status_code==200,r.text
 row=next(x for x in r.json()if x["operation_id"]==ctx["plan"]);assert row["decision_revision"]==2 and row["target_tt_id"]==trip and row["original_target_trip_id"]==old,row
 q.execute("select count(*),sum(BASE_QTY),min(UNIT_VERSION),max(UNIT_VERSION)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'",u=ctx["uid"]);assert q.fetchone()==(3,3,7,7)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 ctx.update(original_target_trip=old,target_trip=trip,original_outbound=old_dock,outbound=dock,decision_operation=winner["operation_id"])
 print("CONTEXT239:"+json.dumps(ctx))
 print("PASS239 WAIT/replay/conflict/DEFER/native rollback/concurrent revision winner/original plan immutable/current routing/both expected departure blocks/existing queue/no quantity/version/protected20/20")
