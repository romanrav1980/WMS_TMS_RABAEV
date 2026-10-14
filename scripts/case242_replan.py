"""Use the already committed source230, no new source shipment."""
import sys,json
from pathlib import Path
import oracledb,httpx
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts
from app.modules.platform.public import read_oracle_json
s=get_settings();ctx=json.loads(Path("tmp/context242.json").read_text(encoding="utf-8"));tag=ctx["tag"];uid=ctx["uid"];cell="QI242"+tag
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
 # Own242 temperature rows already committed before first placement attempt.
 # Own242 temperature rows already committed before first placement attempt.
 thermal={"operation_id":"IW242.MODE:"+tag,"plan_operation_id":ctx["plan"],"decision_kind":"PROCEED","expected_revision":0,"observed_c":"3","task_temp_min":"2","task_temp_max":"4","observation_reference":"Own manual act "+tag,"reason":"Own original task mode","decision_reference":"IW242:"+tag}
 api("POST","/api/inventory/interwarehouse/temperature-decisions",thermal)
 q.execute("select a.BARCODE_SHT from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL where p.UID_PALLET=:u",u=uid);barcode=q.fetchone()[0]
 q.execute("select SYSTEM_CODE,PROFILES_JSON,RAW_CODE from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u order by SYSTEM_CODE,CODE_HASH",u=uid);scans=[]
 for system,profiles,raw in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":raw.read()if hasattr(raw,"read")else raw})
 api("POST","/api/inventory/interwarehouse/unload",{"operation_id":"IW242.UNLOAD:"+tag,"plan_operation_id":ctx["plan"],"scan_pallet":uid,"scan_vehicle":"QL"+tag,"scan_dock":ctx["inbound"]})
 receipt="IW242.RECEIVE:"+tag
 api("POST","/api/inventory/interwarehouse/receive",{"operation_id":receipt,"plan_operation_id":ctx["plan"],"scan_pallet":uid,"scan_cell":cell,"scan_article":barcode,"article":ctx["article"],"quantity":"3","base_uom":"EA","scans":scans})
 placed=api("POST","/api/inventory/interwarehouse/placement",{"operation_id":"IW242.PLACE:"+tag,"receipt_operation_id":receipt});task=placed["task_id"]
 old_task=task
 api("POST","/api/inventory/interwarehouse/temperature-decisions",{**thermal,"operation_id":"IW242.NEW.MODE:"+tag,"expected_revision":1,"task_temp_min":"2.5","task_temp_max":"3.5","reason":"Own narrowed administrative task mode"})
 replan={"operation_id":"IW242.REPLAN:"+tag,"receipt_operation_id":receipt,"superseded_task_id":old_task,"replan_reason":"Own exact changed task range; old task unstarted"}
 refused=api("POST","/api/inventory/interwarehouse/placement",replan,409);assert "CELL_TEMPERATURE_INCOMPATIBLE"in json.dumps(refused),refused
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=old_task);assert q.fetchone()[0]=="PLANNED"
 meta("update RRL_RECEIPT_CELL_RULE set TEMP_MIN=2.5,TEMP_MAX=3.5 where WARE_ID=:w and CELL=:cell",w=ctx["target_ware"],cell=ctx["outbound"])
 actor="WR242"+tag;group=actor.upper();secret=uuid4().hex
 meta("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own replan receiver',:g,:w,0,0)",a=actor,p=secret,g=group,w=ctx["target_ware"])
 for permission in["interwarehouse_receive","warehouse_task_edit"]:meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,:p)",g=group,p=permission)
 own=httpx.Client(auth=(actor,secret),timeout=35)
 rolled={"contract_version":2,"operation_id":"IW242.ROLLBACK:"+tag,"command_type":"INTERWARE_PUTAWAY_PLAN","actor":actor,"source":{"receipt_operation_id":receipt},"lines":[],"units":[],"metadata":{"superseded_task_id":old_task,"replan_reason":replan["replan_reason"]}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(rolled),actor,out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  c.rollback()
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=old_task);assert q.fetchone()[0]=="PLANNED"
 q.execute("select count(*)from RRL_INTERWARE_PUT_PLAN where RECEIPT_OPERATION_ID=:r",r=receipt);assert q.fetchone()[0]==1
 def contender(i):
  body={**replan,"operation_id":"IW242.REPLAN:"+tag+str(i)}
  r=own.post(base+"/api/inventory/interwarehouse/placement",json=body);return body,r
 with ThreadPoolExecutor(2)as pool:attempts=list(pool.map(contender,[1,2]))
 assert sorted(r.status_code for _,r in attempts)==[200,409],[(r.status_code,r.text[:2400])for _,r in attempts]
 winner,response=next(x for x in attempts if x[1].status_code==200);saved=response.json();task=saved["task_id"]
 assert saved["superseded_task_id"]==old_task and saved["temperature"]["task_temp_min"]==2.5 and saved["temperature"]["task_temp_max"]==3.5
 repeated=own.post(base+"/api/inventory/interwarehouse/placement",json=winner);assert repeated.status_code==200 and repeated.json()==saved,repeated.text
 q.execute("select STATUS,CANCELLED_BY from RRL_WAREHOUSE_TASK where TASK_ID=:t",t=old_task);assert q.fetchone()==("CANCELLED",actor)
 q.execute("select TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID=:t",t=old_task);assert q.fetchone()==(2,4)
 q.execute("select TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID=:t",t=task);assert q.fetchone()==(2.5,3.5)
 q.execute("select count(*)from RRL_INTERWARE_PUT_PLAN ip join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=ip.TASK_ID where ip.RECEIPT_OPERATION_ID=:r and wt.STATUS!='CANCELLED'",r=receipt);assert q.fetchone()[0]==1
 meta("delete from RIGHTS where USER_GROUP=:g and upper(RIGHT1)='WAREHOUSE_TASK_EDIT'",g=group)
 denied=own.post(base+"/api/inventory/interwarehouse/placement",json=winner);assert denied.status_code==403,denied.text
 meta("insert into RIGHTS(USER_GROUP,RIGHT1)values(:g,'warehouse_task_edit')",g=group)
 denied=own.post(base+"/api/inventory/interwarehouse/placement",json={**replan,"operation_id":"IW242.OLD.AGAIN:"+tag});assert denied.status_code==409,denied.text
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(3,0)
 print("REPLAN242",old_task,task,"current scoped receiver/currentedit before cached/old2-4/new2.5-3.5/P3H0/native rollback/concurrent one winner/replay/no double plan",flush=True)
 meta("update RUSERS set DELETED=1 where ID=:a",a=actor)
 command={"contract_version":2,"operation_id":"IW242.TASK:"+tag,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":cell,"scanned_to_cell":ctx["outbound"]}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  c.commit()
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 api("POST","/api/inventory/interwarehouse/release-custody",{"operation_id":"IW242.CUSTODY:"+tag,"receipt_operation_id":receipt})
 onward=api("POST","/api/inventory/interwarehouse/prepare-onward",{"operation_id":"IW242.ONWARD:"+tag,"receipt_operation_id":receipt,"reason":"Own242 original marked unit disposition destination","decision_reference":"IW242:"+tag,"accept_legacy_address":True})
 assign_sts(OracleGateway(),ctx["target_trip"],[onward["st_number"]],"admin");st=onward["shipment_identifier"]
 quality=api("GET","/api/outgoing-quality/"+st)
 api("POST","/api/outgoing-quality/"+st+"/scan",{"operation_id":"IW242.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
 preview=api("GET","/api/transport/loading/single-preview?shipment_identifier="+st)
 api("POST","/api/transport/loading/confirm-single",{"operation_id":"IW242.LOAD:"+tag,"identifier":st,"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":ctx["outbound"],"transport_task_id":ctx["target_trip"],"scan_vehicle":"QL"+tag,"scan_dock":ctx["outbound"],"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}})
 api("POST",f"/api/transport/loading/{ctx['target_trip']}/depart",{"operation_id":"IW242.DEPART:"+tag})
 print("PASS242 atomic original task replan/old cancelled/new one task/changed range/new old-native complete/QC/load-depart/same3units6codes/protected");
 print("READY242",tag,uid,"original source reused/current fixed plan3/receipt3/putaway",task,"secondST",onward["st_id"],"second departed/original stock0 and units3 ISSUED10",flush=True)
