"""167 isolated one-unit CASE through real API, close rollback/replay; root cleanup only."""
import sys,json,re
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
from app.services.picking_service import PickingService
from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
from app.modules.inventory.public import CaseCarrierCloseRequest,close_existing_case_carrier
from app.modules.resources.public import assert_case_task_access
import app.modules.inventory.infrastructure.case_carrier_close as closing
s=get_settings();tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:10];ware=20000000+int(tag[:6],16);article="QW193"+tag.upper()
lot="CASE193.QA:"+tag+":"+uuid4().hex[:6];src="Q167S"+tag;dst="Q167D"+tag;wave=None;case=None;plans=[];revision=None;booking=None
api=httpx.Client(auth=("admin","admin123"),timeout=30);base="http://127.0.0.1:8088/api/case-pick"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 def meta(sql,**binds):
  for key in sorted(binds,key=len,reverse=True):sql=re.sub(":"+re.escape(key)+r"\b",":p_"+key,sql)
  binds={"p_"+key:value for key,value in binds.items()}
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def post(kind,metadata,source,op=None):
  from app.modules.inventory.contracts_stock import StockCommand
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  return StockPosting().post(StockCommand(operation_id=op or "QA182:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
 def request(path,body):
  r=api.post(base+path,json=body)
  if r.status_code==503:r=api.post(base+path,json=body)
  assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");template=q.fetchone()[0]
 q.execute("select count(*)from RRL_ARTICULS where ACTICUL=:id",id=article)
 if q.fetchone()[0]==0:
  meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:article;x.BARCODE_SHT:=:barcode;x.ABC_GROUP:='A';x.TYPE_W:=3;x.UNIT_TYPE:='KG';insert into RRL_ARTICULS values x;end;",old=template,article=article,barcode="04012345678901")
  meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)values(:article,'KG','KG',1,1,1,6,'Own182 exact weighted CASE')",article=article)
  meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,UPDATED_BY)values(:article,1,0,0,'admin')",article=article)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:article),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",article=article)
 q.execute("select count(*)from RRL_WARES where ID=:id",id=ware)
 if q.fetchone()[0]==0:
  meta("insert into RRL_WARES(ID,NAME,PREFIX,SPIS_OTBOR_ON_SCAN_OPALL)values(:ware,:name,:prefix,1)",ware=ware,name="Own167 isolated CASE "+tag,prefix="Q"+tag[:2])
  meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:ware,'BOTH',1)",ware=ware)
 for cell in(src,dst,"CPT_"+str(ware)):
  q.execute("select count(*)from RRL_CELLS where CELL=:id and WARE_ID=:ware",id=cell,ware=ware)
  if q.fetchone()[0]==0:
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM)values(:cell,:ware,0,0,0,:pick,:system)",cell=cell,ware=ware,pick=int(cell==dst),system=int(cell.startswith("CPT_")))
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 q.execute("select count(*)from RRL_PICK_FACE f join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=f.PICK_FACE_ID where f.WARE_ID=:ware and f.CELL_CODE=:cell and a.ARTICUL=:article",ware=ware,cell=dst,article=article)
 if q.fetchone()[0]==0:
  face=seq("RRL_PICK_FACE_SQ")
  meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY)values(:id,:ware,:cell,null,'admin')",id=face,ware=ware,cell=dst)
  meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE)values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:article,.24,0,'FULL_PALLET')",face=face,article=article)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 print("Fixture167",tag,"WARE",ware,"SKU",article,"revision",revision,flush=True)
 try:
  labels=["(01)04012345678901(3103)009800(21)"+tag+str(i)for i in range(2)]
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":dst,"article":article,"quantity":"20","expiry_date":"2030-01-01","price":0,"reason":"Own193 loose unmarked KG"},{"revision_id":revision})
  q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0];order=seq("RRL_CUSTOMER_ORDER_SQ")
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,:number,:customer,:ware)",id=order,number=lot,customer=customer,ware=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:order_id,1,:article,10,'KG')",order_id=order,article=article)
  picking=PickingService();plan=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
  q.execute("select TASK_TYPE from RRL_PICK_TASK where PICK_PLAN_ID=:id",id=plan);assert q.fetchone()[0]=="CASE_PICK"
  wave=picking.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=ware,created_by="admin"))
  picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="QA167.LAUNCH:"+str(wave)))
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:id and STATUS not in('DONE','CANCELLED')",id=wave)
  for task,uid,from_cell,to_cell,qty in q.fetchall():
   post("TASK_COMPLETE",{"fact_qty":str(qty),"scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:id",id=wave)
  case,line,carrier,cell=q.fetchone();case,line=int(case),int(line)
  q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);case_type=q.fetchone()[0]
  tare_base="http://127.0.0.1:8088/api/inventory/tare"
  availability=api.get(tare_base+f"/warehouses/{ware}/availability");assert availability.status_code==200,availability.text[:1200]
  current=next(row for row in availability.json()if row["pallet_type_id"]==case_type)
  observed=api.post(tare_base+"/count",json={"operation_id":"QA167.TARE.COUNT:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,
      "condition":"GOOD","observed_quantity":"1","expected_version":current["balance_version"] or 0,
      "reason":"Own software fixture container observation, no hardware acceptance","decision_reference":"QA167:"+str(case)})
  assert observed.status_code==200,(observed.status_code,observed.text[:1300])
  booking="QA167.TARE.BOOK:"+str(case)
  booked=api.post(tare_base+"/book",json={"operation_id":booking,"place_kind":"CASE","place_id":str(case)})
  assert booked.status_code==200,(booked.status_code,booked.text[:1300])
  request(f"/tasks/{case}/claim",{});request(f"/tasks/{case}/start",{})
  sender="QS193"+tag;group=sender.upper();secret=uuid4().hex;device="WH.SCALE193:"+tag
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own warehouse scale gateway',:grp,:ware,0,0)",id=sender,secret=secret,grp=group,ware=ware);c.commit()
  def scale_call(client,method,path,body=None,status=200):
   r=client.request(method,"http://127.0.0.1:8088"+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
  scale_call(api,"POST","/api/admin/rights/groups",{"id":group,"name":"Own193 addressed scale sender"})
  scale_call(api,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"warehouse_scale_ingest","description":"Own software gateway"})
  def stamp(value):return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
  now=datetime.now(timezone.utc);scale_base="/api/inventory/warehouse-scales"
  policy={"warehouse_id":ware,"post_cell":dst,"sender_id":sender,"expected_version":0,"active":True,"device_mode":"TEST","basis":"NET","capacity_kg":"100","resolution_kg":"0.01","calibration_ref":"DEV193:"+tag,"calibrated_until":stamp(now+timedelta(days=1))}
  scale_call(api,"PUT",scale_base+"/devices/"+device,policy)
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);content_version=int(q.fetchone()[0])
  now=datetime.now(timezone.utc)
  packet={"device_id":device,"capture_id":"SAMPLE193:"+tag,"post_cell":dst,"case_task_id":case,"case_line_id":line,
   "expected_content_version":content_version,"scan_source_cell":cell,"scan_container":carrier,"scan_product":article,"device_policy_version":1,"calibration_ref":policy["calibration_ref"],
   "unit":"KG","basis":"NET","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=60)),"measured_at":stamp(now),
   "samples":[{"offset_ms":i*500,"weight_kg":"9.6"}for i in range(5)]}
  gateway=httpx.Client(auth=(sender,secret),timeout=30)
  scale_call(gateway,"POST",scale_base+"/captures",{**packet,"capture_id":"BAD193:"+tag,"samples":[*packet["samples"][:-1],{"offset_ms":2000,"weight_kg":"9.63"}]},409)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:w",w=ware);stock_before=q.fetchone()
  capture=scale_call(gateway,"POST",scale_base+"/captures",packet);assert capture["weight_kg"]=="9.6"and capture["device_mode"]=="TEST"and not capture["stock_posted"]
  assert scale_call(gateway,"POST",scale_base+"/captures",packet)==capture
  scale_call(gateway,"POST",scale_base+"/captures",{**packet,"zero_check_kg":"0.01"},409)
  assert scale_call(api,"GET",scale_base+"/captures/"+capture["capture_key"])==capture
  archived=scale_call(api,"GET",scale_base+f"/captures?task={case}&line={line}");assert archived["items"]==[capture]
  scale_call(api,"POST",scale_base+"/captures",packet,403)
  scale_call(gateway,"GET",scale_base+"/captures/"+capture["capture_key"],status=403)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:w",w=ware);assert q.fetchone()==stock_before
  try:q.execute("delete RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key",p_key=capture["capture_key"]);raise AssertionError("Original scale capture deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  print("PASS193 current warehouse/address/CASE/version/dedicated sender/stable original10.1KG/TEST mode/hash/replay/conflict/unstable/foreign rights/append-only/no P-H effect",capture["capture_key"],flush=True)
  operation="CASE.WEIGHT182:"+str(case)
  body={"operation_id":operation,"scan_cell":cell,"scan_container":carrier,"warehouse_scale_capture":capture["capture_key"]}
  result=request(f"/tasks/{case}/lines/{line}/weigh-line",body)
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);journal=q.fetchone();assert journal[0]>0
  q.execute("select STOCK_OPERATION_ID from RRL_WH_SCALE_USE where CAPTURE_KEY=:p_key",p_key=capture["capture_key"]);assert q.fetchone()==(operation,)
  reused=api.post(base+f"/tasks/{case}/lines/{line}/weigh-line",json={**body,"operation_id":operation+":SECOND"});assert reused.status_code==409,(reused.status_code,reused.text)
  assert request(f"/tasks/{case}/lines/{line}/weigh-line",body)==result
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);assert q.fetchone()==journal
  changed=api.post(base+f"/tasks/{case}/lines/{line}/weigh-line",json={**body,"scan_container":carrier+":CHANGED"});assert changed.status_code==409
  q.execute("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:id",id=line);assert str(q.fetchone()[0])=="9.6"
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);p,h=q.fetchone();assert round(p,1)==20 and round(h,1)==10
  q.execute("select STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()==("PARTIAL",)
  reported=request(f"/tasks/{case}/lines/{line}/short",{"picked_qty":"9.6","short_qty":"0.4",
    "reason_text":"Exact stable NET within configured order tolerance","offline_event_id":"WEIGHT193.REPORT:"+tag})
  short_id=int(reported["case_pick_short_id"])
  preview_response=api.get(base+f"/tasks/{case}/lines/{line}/order-weight-preview");assert preview_response.status_code==200,preview_response.text
  preview=preview_response.json();assert preview["within_tolerance"]
  approval={"operation_id":"WEIGHT193.DECIDE:"+tag,"decision":"WEIGHT_TOLERANCE","reason_text":"Accept exact9.6KG against original10KG within15 percent",
    "expected_weight_policy_version":preview["policy_version"],"expected_content_version":preview["content_version"],
    "expected_order_weight_signature":preview["order_weight_signature"]}
  denied=api.post(base+f"/shorts/{short_id}/approve",json={**approval,"operation_id":approval["operation_id"]+":STALE","expected_order_weight_signature":"0"*64})
  assert denied.status_code==409,(denied.status_code,denied.text)
  metadata={"reason":approval["reason_text"],"decision":"WEIGHT_TOLERANCE","expected_weight_policy_version":approval["expected_weight_policy_version"],
    "expected_content_version":approval["expected_content_version"],"expected_order_weight_signature":approval["expected_order_weight_signature"]}
  command={"contract_version":2,"operation_id":approval["operation_id"],"command_type":"CASE_SHORT_APPROVE","actor":"admin",
    "source":{"short_id":short_id},"lines":[],"units":[],"metadata":metadata}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  key="STOCK:"+sha256(approval["operation_id"].encode()).hexdigest().upper()
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select STATUS,WEIGHT_DECISION_OPERATION,INVENTORY_TASK_ID from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);assert q.fetchone()==("ACCEPTED",approval["operation_id"],None)
   q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:p_key",p_key=key);assert q.fetchone()==(1,)
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS,WEIGHT_DECISION_OPERATION from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);assert q.fetchone()==("PENDING_APPROVAL",None)
  q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:p_key",p_key=key);assert q.fetchone()==(0,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(20,10)
  def approve():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    r=client.post(base+f"/shorts/{short_id}/approve",json=approval);assert r.status_code==200,(r.status_code,r.text);return r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:decisions=list(pool.map(lambda _:approve(),range(2)))
  assert decisions[0]==decisions[1]and decisions[0]["inventory_task_id"]is None
  q.execute("select WEIGHT_POLICY_VERSION,WEIGHT_TOLERANCE_PCT,WEIGHT_ORDER_REQUESTED_KG,WEIGHT_ORDER_PICKED_KG,WEIGHT_DECISION_OPERATION from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id)
  policy_version,pct,original,actual,decision_op=q.fetchone();assert(policy_version,pct,original,actual,decision_op)==(1,15,10,9.6,approval["operation_id"])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(20,9.6)
  q.execute("select PICKED_QTY,STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()==(9.6,"SHORT_PICKED")
  try:q.execute("update RRL_CASE_PICK_SHORT set WEIGHT_TOLERANCE_PCT=100 where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);raise AssertionError("Original approval changed")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  q.execute("select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:p_order and ARTICUL=:p_article",p_order=order,p_article=article);original_row=int(q.fetchone()[0])
  demand=read_oracle_json(q.callfunc("RRL_STOCK_POOL_READ.line_snapshot_json",oracledb.DB_TYPE_CLOB,[original_row]))
  assert demand["requested_base_quantity"]=="10"and demand["picked_quantity"]=="9.6"and demand["hard_quantity"]=="9.6"
  assert demand["accepted_weight_deviation_quantity"]==".4"or demand["accepted_weight_deviation_quantity"]=="0.4",demand
  assert demand["quantity"]=="0"and demand["quantity_semantics"]=="UNALLOCATED_BASE_AFTER_ACCEPTED_WEIGHT_DEVIATION",demand
  print("PASS193 accepted current deviation.4 suppresses repeat demand; original10/actual9.6/H9.6 remain explicit",flush=True)
  print("PASS193 exact9.6/10 within15 explicit signed approval/no inventory discrepancy/P20H9.6/SHORT_PICKED/outer rollback outbox+decision+reserve/concurrent saved replay/stale409/immutable proof",approval["operation_id"],short_id,flush=True)
  print("PASS193 loose NET9.6/current KG unmarked/root exact saved replay/once-only USE/changed request409/P20H10/CASE PARTIAL remaining.4 preserved",operation,flush=True)
 finally:
  if wave is not None:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:id",id=wave)
   for task,carrier,version in q.fetchall():
    q.execute("select h.LOT_UID from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_TASK_ID=:id and exists(select 1 from RRL_REMAINS r where r.UID_POLETA=h.LOT_UID and r.REMAIN>0)",id=task);lots=[row[0]for row in q.fetchall()]
    post("CASE_CARRIER_RETURN",{"destinations":{uid:dst for uid in lots},"allow_empty":not bool(lots),"scan_container":carrier,"expected_content_version":int(version),"reason":"Own167 cleanup after preserved proof"},{"case_task_id":int(task)})
   if "original_row"in locals():
    reopened=read_oracle_json(q.callfunc("RRL_STOCK_POOL_READ.line_snapshot_json",oracledb.DB_TYPE_CLOB,[original_row]))
    assert reopened["accepted_weight_deviation_quantity"]=="0"and reopened["picked_quantity"]=="0"and reopened["quantity"]=="10",reopened
    q.execute("select STATUS,WEIGHT_DECISION_OPERATION from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:p_short",p_short=short_id);assert q.fetchone()==("ACCEPTED",approval["operation_id"])
    print("PASS193 native CASE return removes current waiver/reopens original10, immutable approval retained",flush=True)
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:id and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",id=wave)
   for(reservation,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Own167 cleanup"},{"reservation_id":int(reservation)})
  if booking is not None:
   cancelled=api.post(tare_base+"/book-cancel",json={"operation_id":"QA167.TARE.CANCEL:"+str(case),"booking_operation_id":booking})
   assert cancelled.status_code==200,(cancelled.status_code,cancelled.text[:1300])
   availability=api.get(tare_base+f"/warehouses/{ware}/availability")
   current=next(row for row in availability.json()if row["pallet_type_id"]==case_type)
   observed=api.post(tare_base+"/count",json={"operation_id":"QA167.TARE.ZERO:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,
       "condition":"GOOD","observed_quantity":"0","expected_version":current["balance_version"] or 0,
       "reason":"Retire owned empty software fixture container","decision_reference":"QA167.END:"+str(case)})
   assert observed.status_code==200,(observed.status_code,observed.text[:1300])
  if wave is not None:
   q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:id",id=wave)
   if q.fetchone()[0] != "LAUNCHED":
    post("WAVE_CANCEL",{"reason":"Retire owned182 unlaunched fixture"},{"document_type":"PICK_WAVE","document_id":wave})
   else:post("WAVE_EXECUTION_FINISH",{"disposition":"RETURNED_TO_PLANNING","reason":"Owned182 native carrier return/tare release; demand remains"},{"wave_id":wave})
  def physical_keys(uid,cell):
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE'",u=uid,c=cell);return [r[0]for r in q.fetchall()]
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:article and r.REMAIN>0",article=article)
  counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":physical_keys(uid,cell)}for uid,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End owned isolated one-unit CASE case","counts":counts},{"revision_id":revision})
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own167 P/H cleared through native return/release/count; original135 P20H20 unchanged; history retained",flush=True)

with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as done:
 done.cursor().execute("update RUSERS set DELETED=1 where ID=:p_sender",p_sender=sender);done.commit()
