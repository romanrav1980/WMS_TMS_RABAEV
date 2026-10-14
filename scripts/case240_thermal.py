"""Use the already committed source230, no new source shipment."""
import sys,json
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts
from app.modules.platform.public import read_oracle_json
s=get_settings();ctx=json.loads(Path("tmp/context240.json").read_text(encoding="utf-8"));tag=ctx["tag"];uid=ctx["uid"];cell="QI240"+tag
h=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
def api(method,path,body=None,status=200):
 r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:3000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 for name,blocked in[(cell,1),(ctx["outbound"],0)]:
  q.execute("select count(*)from RRL_CELLS where CELL=:n",n=name)
  if not q.fetchone()[0]:
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:n,:w,0,0,0,0,0,0,0,0,:b,:b)",n=name,w=ctx["target_ware"],b=blocked)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:n),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",n=name)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:w,:a,:cell,2,4)",w=ctx["target_ware"],a=ctx["article"],cell=ctx["outbound"])
 meta("insert into RRL_RECEIPT_CELL_RULE(WARE_ID,CELL,TEMP_MIN,TEMP_MAX)values(:w,:cell,2,4)",w=ctx["target_ware"],cell=ctx["outbound"])
 thermal={"operation_id":"IW240.HOLD:"+tag,"plan_operation_id":ctx["plan"],"decision_kind":"HOLD","expected_revision":0,"observed_c":"8.125","observation_reference":"Own manual act "+tag,"reason":"Own manual deviation awaiting dispatcher decision","decision_reference":"IW240:"+tag}
 held=api("POST","/api/inventory/interwarehouse/temperature-decisions",thermal);assert held["revision"]==1 and held["observed_c"]==8.125 and not held["stock_changed"]and not held["sensor_verified"],held
 assert api("POST","/api/inventory/interwarehouse/temperature-decisions",thermal)==held
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**thermal,"reason":"changed"},409)
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=uid);barcode=q.fetchone()[0]
 q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid);scans=[]
 for system,profiles,raw in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 api("POST","/api/inventory/interwarehouse/unload",{"operation_id":"IW240.UNLOAD:"+tag,"plan_operation_id":ctx["plan"],"scan_pallet":uid,"scan_vehicle":"QL"+tag,"scan_dock":ctx["inbound"]})
 receipt="IW240.RECEIVE:"+tag
 api("POST","/api/inventory/interwarehouse/receive",{"operation_id":receipt,"plan_operation_id":ctx["plan"],"scan_pallet":uid,"scan_cell":cell,"scan_article":barcode,"article":ctx["article"],"quantity":"3","base_uom":"EA","scans":scans})
 denied=api("POST","/api/inventory/interwarehouse/placement",{"operation_id":"IW240.EARLY:"+tag,"receipt_operation_id":receipt},409);assert "INTERWARE_TEMPERATURE_DISPATCHER_HOLD"in json.dumps(denied),denied
 denied=api("POST",f"/api/transport/loading/{ctx['target_trip']}/depart",{"operation_id":"IW240.EARLY.DEPART:"+tag},409);assert "INTERWARE_TEMPERATURE_DISPATCHER_HOLD"in json.dumps(denied),denied
 proceed={**thermal,"operation_id":"IW240.PROCEED:"+tag,"decision_kind":"PROCEED","expected_revision":1,"task_temp_min":"2","task_temp_max":"4","reason":"Own administrative quality disposition; preserve approved task range"}
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**proceed,"operation_id":"IW240.BAD.RANGE:"+tag,"task_temp_min":"1","task_temp_max":"6"},409)
 rolled={**proceed,"operation_id":"IW240.ROLLBACK:"+tag,"actor":"admin"}
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:q.callproc("RRL_INTERWARE_THERMAL.record_decision",[json.dumps(rolled,sort_keys=True,separators=(",",":")),"admin",out]);c.rollback()
 finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select count(*)from RRL_INTERWARE_THERMAL_FACT where OPERATION_ID=:op",op=rolled["operation_id"]);assert q.fetchone()[0]==0
 released=api("POST","/api/inventory/interwarehouse/temperature-decisions",proceed);assert released["revision"]==2 and released["task_temp_min"]==2 and released["task_temp_max"]==4,released
 placed=api("POST","/api/inventory/interwarehouse/placement",{"operation_id":"IW240.PLACE:"+tag,"receipt_operation_id":receipt});task=placed["task_id"]
 q.execute("select TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID=:id",id=task);assert q.fetchone()==(proceed["operation_id"],2,4)
 # HOLD after task creation prevents original native movement; later same-range release retains task mode.
 stop={**thermal,"operation_id":"IW240.TASK.HOLD:"+tag,"expected_revision":2}
 api("POST","/api/inventory/interwarehouse/temperature-decisions",stop)
 denied_command={"contract_version":2,"operation_id":"IW240.TASK.EARLY:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":cell,"scanned_to_cell":ctx["outbound"]}}
 denied_out=q.var(oracledb.DB_TYPE_CLOB)
 try:q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(denied_command),"admin",denied_out,None]);raise AssertionError("thermal HOLD movement escaped")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20886 and "TEMPERATURE_DISPATCHER_HOLD"in str(exc),str(exc)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**proceed,"operation_id":"IW240.TASK.PROCEED:"+tag,"expected_revision":3})
 command={"contract_version":2,"operation_id":"IW240.TASK:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":cell,"scanned_to_cell":ctx["outbound"]}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  c.commit()
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 api("POST","/api/inventory/interwarehouse/release-custody",{"operation_id":"IW240.CUSTODY:"+tag,"receipt_operation_id":receipt})
 onward=api("POST","/api/inventory/interwarehouse/prepare-onward",{"operation_id":"IW240.ONWARD:"+tag,"receipt_operation_id":receipt,"reason":"Own240 original marked unit disposition destination","decision_reference":"IW240:"+tag,"accept_legacy_address":True})
 assign_sts(OracleGateway(),ctx["target_trip"],[onward["st_number"]],"admin");st=onward["shipment_identifier"]
 quality=api("GET","/api/outgoing-quality/"+st)
 api("POST","/api/outgoing-quality/"+st+"/scan",{"operation_id":"IW240.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
 preview=api("GET","/api/transport/loading/single-preview?shipment_identifier="+st)
 api("POST","/api/transport/loading/confirm-single",{"operation_id":"IW240.LOAD:"+tag,"identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":ctx["outbound"],"transport_task_id":ctx["target_trip"],"scan_vehicle":"QL"+tag,"scan_dock":ctx["outbound"],"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}})
 api("POST",f"/api/transport/loading/{ctx['target_trip']}/depart",{"operation_id":"IW240.DEPART:"+tag})
 print("PASS240 manual HOLD/replay/conflict/known SKU range/native rollback/receipt blocked cell/P3/original task mode preserved/HOLD after planned prevents native move/same-range release/old complete-QC-load-depart/current original3units6codes");
 print("READY240",tag,uid,"original source reused/current fixed plan3/receipt3/putaway",task,"secondST",onward["st_id"],"second departed/original stock0 and units3 ISSUED10",flush=True)
