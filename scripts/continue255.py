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
s=get_settings();ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));tag=ctx["tag"];uid=ctx["uid"];cell="QI255"+tag
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
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=uid);barcode=q.fetchone()[0]
 q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid);scans=[]
 for system,profiles,raw in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 api("POST","/api/inventory/interwarehouse/unload",{"operation_id":"IW255.UNLOAD:"+tag,"plan_operation_id":ctx["plan"],"scan_pallet":uid,"scan_vehicle":"QL"+tag,"scan_dock":ctx["inbound"]})
 receipt="IW255.RECEIVE:"+tag
 api("POST","/api/inventory/interwarehouse/receive",{"operation_id":receipt,"plan_operation_id":ctx["plan"],"scan_pallet":uid,"scan_cell":cell,"scan_article":barcode,"article":ctx["article"],"quantity":"3","base_uom":"EA","scans":scans})
 placed=api("POST","/api/inventory/interwarehouse/placement",{"operation_id":"IW255.PLACE:"+tag,"receipt_operation_id":receipt});task=placed["task_id"]
 command={"contract_version":2,"operation_id":"IW255.TASK:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":cell,"scanned_to_cell":ctx["outbound"]}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  c.commit()
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 from app.modules.transport.public import TransportPreflight,generate_existing_operations
 coordination=TransportPreflight(OracleGateway())
 after_place=coordination.coordination(ctx["target_trip"],"admin")
 assert after_place["warehouse_placed_deliveries"]==1
 assert not any(x["code"]in("COORDINATION_WAREHOUSE_PLACEMENT_PENDING","COORDINATION_READY_PROMISE_AFTER_LOADING")for x in after_place["blockers"]),after_place
 assert any(x["code"]=="COORDINATION_ORIGINAL_ST_MEMBERS_REQUIRED"for x in after_place["blockers"])
 api("POST","/api/inventory/interwarehouse/release-custody",{"operation_id":"IW255.CUSTODY:"+tag,"receipt_operation_id":receipt})
 onward=api("POST","/api/inventory/interwarehouse/prepare-onward",{"operation_id":"IW255.ONWARD:"+tag,"receipt_operation_id":receipt,"reason":"Own243 original marked unit disposition destination","decision_reference":"IW255:"+tag,"accept_legacy_address":True})
 assign_sts(OracleGateway(),ctx["target_trip"],[onward["st_number"]],"admin");st=onward["shipment_identifier"]
 # Actual membership invalidates old empty-TT approval; current source regeneration/approval required.
 changed=coordination.time_context(ctx["target_trip"],"admin")
 assert changed["approval_status"]=="SOURCE_CHANGED"
 generate_existing_operations(OracleGateway(),ctx["target_trip"],"admin")
 source=coordination.time_context(ctx["target_trip"],"admin")
 coordination.approve_time("TIME255.MEMBERS:"+tag,{"trip_id":ctx["target_trip"],"expected_version":source["version"],"source_hash":source["source_hash"],"time_zone":"UTC","reason":"Own255 original received member current loading plan"},"admin")
 quality=api("GET","/api/outgoing-quality/"+st)
 api("POST","/api/outgoing-quality/"+st+"/scan",{"operation_id":"IW255.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
 preview=api("GET","/api/transport/loading/single-preview?shipment_identifier="+st)
 api("POST","/api/transport/loading/confirm-single",{"operation_id":"IW255.LOAD:"+tag,"identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":ctx["outbound"],"transport_task_id":ctx["target_trip"],"scan_vehicle":"QL"+tag,"scan_dock":ctx["outbound"],"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}})
 complete=coordination.coordination(ctx["target_trip"],"admin")
 assert complete["warehouse_placed_deliveries"]==1 and complete["incoming"]["incoming_ready"]and complete["loading"]["all_members_physically_loaded"]
 # Loading changes source membership CONDITION; prior approval correctly becomes SOURCE_CHANGED.
 assert complete["time"]["approval_status"]=="SOURCE_CHANGED"
 assert any(x["code"]=="COORDINATION_TIME_NOT_CURRENT_APPROVED"for x in complete["blockers"])
 assert not complete["operational_admission"]and not complete["departure_authorized"]
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.get(base+f"/api/transport/preflight/trips/{ctx['target_trip']}/coordination")
  assert r.status_code==200 and r.json()["warehouse_placed_deliveries"]==1
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like 'with candidates as(%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
 ctx["task255"]=task;ctx["st255"]=onward;Path("tmp/context254.json").write_text(json.dumps(ctx,ensure_ascii=True),encoding="utf-8")
 print("PASS255 original same3units6codes received/putaway/custody/nativeST assigned/QC/load only; placed0→1 clears predictionlate promise; current member approval invalidates after loading/sourcechanges honest BLOCKED/no admission/HTTP/protected20-20/target remains LOADED for next publish source fix",flush=True)
