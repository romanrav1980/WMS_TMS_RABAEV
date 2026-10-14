"""167 isolated one-unit CASE through real API, close rollback/replay; root cleanup only."""
import sys,json,re
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
s=get_settings();tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:10];ware=20000000+int(tag[:6],16);article="QW196"+tag.upper()
lot="CASE196.QA:"+tag+":"+uuid4().hex[:6];src="Q167S"+tag;dst="Q167D"+tag;wave=None;case=None;plans=[];revision=None;booking=None
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
  meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,UPDATED_BY)values(:article,1,0,1,'admin')",article=article)
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
  meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY)values(:id,:ware,:cell,.2,'admin')",id=face,ware=ware,cell=dst)
  meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE)values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:article,.24,0,'FULL_PALLET')",face=face,article=article)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 print("Fixture167",tag,"WARE",ware,"SKU",article,"revision",revision,flush=True)
 try:
  labels=["(01)04012345678901(3103)008000(21)"+tag+"0","(01)04012345678901(3103)012000(21)"+tag+"1"]
  boxes=[{"barcode":labels[0],"codes":[],"gross_weight_kg":"8.3","volume_m3":"0.024","measurement_reference":"Own195 actual box8"},
         {"barcode":labels[1],"codes":[],"gross_weight_kg":"12.3","volume_m3":"0.036","measurement_reference":"Own195 actual box12"}]
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"20","expiry_date":"2030-01-01","price":0,"reason":"Own195 actual whole boxes8/12",
    "birth_captures":{lot:{"capture_mode":"WEIGHTED_BOXES","policy_version":1,"weighted_boxes":boxes}}},{"revision_id":revision})
  q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0];order=seq("RRL_CUSTOMER_ORDER_SQ")
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,:number,:customer,:ware)",id=order,number=lot,customer=customer,ware=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:order_id,1,:article,10,'KG')",order_id=order,article=article)
  q.execute("select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:p_order and ARTICUL=:p_article",p_order=order,p_article=article);row=int(q.fetchone()[0])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);before=q.fetchone();assert before==(20,0)
  path="http://127.0.0.1:8088/api/picking/order-rows/"+str(row)+"/weighted-box-options"
  answer=api.get(path);assert answer.status_code==200,(answer.status_code,answer.text);options=answer.json()
  assert options["requested_order_quantity"]=="10"and options["remaining_row_quantity"]=="10"and options["tolerance_pct"]=="15"
  assert not options["choice_saved"]and options["no_split"]and options["approval_required"]
  assert sorted(x["net_weight_kg"]for x in options["boxes"])==["12","8"]
  assert all(x["exception_required"]and not x["within_tolerance"]and x["measurements_ready"]for x in options["boxes"])
  assert all(x["pallet_identifier"]==lot and x["source_cell"]==src for x in options["boxes"])
  assert api.get(path).json()==options
  try:q.callfunc("RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json",oracledb.DB_TYPE_CLOB,[row,"Q1341a19738325"]);raise AssertionError("Foreign warehouse source exposed")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20882 and "WARE_FORBIDDEN"in str(exc)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==before
  approver="QA196"+tag;group=approver.upper();secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p_id,:p_secret,'Own195 weight exception approver',:p_group,:p_ware,0,0)",
    p_id=approver,p_secret=secret,p_group=group,p_ware=ware);c.commit()
  r=api.post("http://127.0.0.1:8088/api/admin/rights/groups",json={"id":group,"name":"Own195 approval only"});assert r.status_code==200,(r.status_code,r.text)
  r=api.post("http://127.0.0.1:8088/api/admin/rights/groups/"+group+"/rights",json={"right_name":"case_pick_short_approve","description":"Own195 commercial final box decision"});assert r.status_code==200,(r.status_code,r.text)
  manager=httpx.Client(auth=(approver,secret),timeout=30)
  r=manager.get(path);assert r.status_code==403,(r.status_code,r.text)
  approval_path=path.replace("weighted-box-options","weighted-box-approval-preview")
  r=manager.get(approval_path);assert r.status_code==200,(r.status_code,r.text);scope=r.json();assert scope["source_signature"]==options["source_signature"]
  chosen=next(x for x in scope["boxes"]if x["net_weight_kg"]=="8")
  body={"choice_id":"WEIGHT196.CHOICE:"+tag,"customer_order_row_id":row,"physical_unit_key":chosen["physical_unit_key"],
    "weighted_box_barcode":labels[0],"source_signature":scope["source_signature"],"choice_mode":"LAST_WHOLE_BOX",
    "reason":"Approve exact8KG final sealed box against10KG original order; no splitting"}
  choice_url="http://127.0.0.1:8088/api/picking/weighted-box-choices"
  for change in ({"choice_mode":"WITHIN_TOLERANCE"},{"source_signature":"0"*64},{"weighted_box_barcode":labels[1]}):
   r=manager.post(choice_url,json={**body,**change,"choice_id":body["choice_id"]+":BAD:"+uuid4().hex[:4]});assert r.status_code==409,(r.status_code,r.text)
  r=manager.post(choice_url,json=body);assert r.status_code==200,(r.status_code,r.text);accepted=r.json()
  assert accepted["selected_net_weight_kg"]=="8"and accepted["status"]=="ACCEPTED"and not accepted["stock_changed"]and not accepted["plan_created"]
  assert manager.post(choice_url,json=body).json()==accepted
  active=manager.get(approval_path).json();assert active["active_choice"]["choice_id"]==body["choice_id"]and active["active_choice"]["selected_net_weight_kg"]=="8"
  r=manager.post(choice_url,json={**body,"reason":body["reason"]+":CHANGED"});assert r.status_code==409
  r=manager.post(choice_url,json={**body,"choice_id":body["choice_id"]+":OTHER"});assert r.status_code==409,(r.status_code,r.text)
  q.execute("select STATUS,NET_WEIGHT_KG,ORIGINAL_ORDER_KG,TOLERANCE_PCT from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("ACCEPTED",8,10,15)
  try:q.execute("update RRL_PICK_WEIGHT_CHOICE set NET_WEIGHT_KG=12 where CHOICE_ID=:p_id",p_id=body["choice_id"]);raise AssertionError("Original choice rewritten")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  cancel_url=choice_url+"/"+body["choice_id"]+"/cancel";cancel_body={"reason":"Retire own software decision before native fixture cleanup"}
  # Original native planner owns the transaction; outer rollback must remove all projections and binding.
  temporary=int(q.callfunc("RRL_PICKING_API.create_plan",oracledb.DB_TYPE_NUMBER,[order,"FEFO","admin"]))
  q.execute("select STATUS,PICK_PLAN_ID from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("USED",temporary)
  c.rollback()
  q.execute("select STATUS,PICK_PLAN_ID from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("ACCEPTED",None)
  from concurrent.futures import ThreadPoolExecutor
  def create():return PickingService().create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"))
  with ThreadPoolExecutor(max_workers=2)as pool:created=list(pool.map(lambda _:create(),range(2)))
  assert created[0]==created[1],created
  plan=created[0];plans.append(plan)
  q.execute("select STATUS,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);status,bound,line=q.fetchone();assert status=="USED"and bound==plan
  q.execute("select REQUESTED_QTY,PLANNED_QTY from RRL_PICK_PLAN_LINE where PICK_PLAN_LINE_ID=:p_id",p_id=line);assert q.fetchone()==(10,8)
  q.execute("select QTY,PALLET_UID,SOURCE_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_LINE_ID=:p_id",p_id=line);assert q.fetchone()==(8,lot,src)
  q.execute("select sum(RESERVED_QTY)from RRL_PICK_RESERVATION where PICK_PLAN_LINE_ID=:p_id and RESERVATION_STATUS='ACTIVE'and RESERVATION_LEVEL='SOFT'",p_id=line);assert q.fetchone()[0]==8
  from fastapi import HTTPException
  try:PickingService().create_plan(PickingPlanCreateRequest(customer_order_id=order,plan_strategy="FIFO",created_by="admin"));raise AssertionError("Changed strategy accepted")
  except HTTPException as exc:assert exc.status_code==409,(exc.status_code,exc.detail)
  r=manager.post(cancel_url,json=cancel_body);assert r.status_code==409,(r.status_code,r.text)
  PickingService().cancel_plan(plan,"admin")
  r=manager.post(cancel_url,json=cancel_body);assert r.status_code==200,(r.status_code,r.text);cancelled=r.json()
  assert manager.post(cancel_url,json=cancel_body).json()==cancelled
  assert manager.get(approval_path).json()["active_choice"]is None
  q.execute("select STATUS,NET_WEIGHT_KG,SOURCE_SIGNATURE from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=:p_id",p_id=body["choice_id"]);assert q.fetchone()==("CANCELLED",8,scope["source_signature"])
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==before
  q.execute("update RUSERS set DELETED=1 where ID=:p_id",p_id=approver);c.commit()
  print("PASS196 approval-only actor/no plan-create right/current signed exact8-vs10/explicit exception/default15 unchanged/replay/conflicts/wrong label/stale signature/active uniqueness/immutable original/cancel history/no P-H effect",body["choice_id"],flush=True)
  print("PASS196 original10/current whole8or12/exact net gross volume/source/version/default15/exception_required/no_split/stable signed read/current foreignWARE403/P20H0 unchanged",options["source_signature"],flush=True)

 finally:
  if wave is not None:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:id",id=wave)
   for task,carrier,version in q.fetchall():
    q.execute("select h.LOT_UID from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_TASK_ID=:id and exists(select 1 from RRL_REMAINS r where r.UID_POLETA=h.LOT_UID and r.REMAIN>0)",id=task);lots=[row[0]for row in q.fetchall()]
    post("CASE_CARRIER_RETURN",{"destinations":{uid:dst for uid in lots},"allow_empty":not bool(lots),"scan_container":carrier,"expected_content_version":int(version),"reason":"Own167 cleanup after preserved proof"},{"case_task_id":int(task)})
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
  for plan in plans:
   PickingService().cancel_plan(plan,"admin")
  def physical_keys(uid,cell):
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE'",u=uid,c=cell);return [r[0]for r in q.fetchall()]
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:article and r.REMAIN>0",article=article)
  counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":physical_keys(uid,cell)}for uid,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End owned isolated one-unit CASE case","counts":counts},{"revision_id":revision})
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own167 P/H cleared through native return/release/count; original135 P20H20 unchanged; history retained",flush=True)

