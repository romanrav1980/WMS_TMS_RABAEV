"""209 isolated one-unit CASE through real API, close rollback/replay; root cleanup only."""
import sys,json,re
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.services.picking_service import PickingService
from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
from app.modules.inventory.public import CaseCarrierCloseRequest,close_existing_case_carrier
from app.modules.resources.public import assert_case_task_access
import app.modules.inventory.infrastructure.case_carrier_close as closing
s=get_settings();tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:10];ware=20000000+int(tag[:6],16);article="QC209"+tag.upper()
article2=article+"B";dst2="Q209E"+tag;lot2="CASE209.B:"+tag
lot="CASE209.QA:"+tag+":"+uuid4().hex[:6];src="Q209S"+tag;dst="Q209D"+tag;wave=None;case=None;plans=[];revision=None;booking=None
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
  body={"contract_version":2,"operation_id":op or "QA209:"+uuid4().hex,"command_type":kind,"actor":"admin","source":source,"lines":[],"units":[],"metadata":metadata}
  inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(body));out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   raw=out.getvalue();result=json.loads(raw.read()if hasattr(raw,"read")else raw);c.commit();return result
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 def request(path,body):
  r=api.post(base+path,json=body)
  if r.status_code==503:r=api.post(base+path,json=body)
  assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");template=q.fetchone()[0]
 q.execute("select count(*)from RRL_ARTICULS where ACTICUL=:id",id=article)
 if q.fetchone()[0]==0:
  meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:article;x.BARCODE_SHT:=:barcode;x.ABC_GROUP:='A';insert into RRL_ARTICULS values x;end;",old=template,article=article,barcode="BC209"+tag)
  meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :article,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own209 HTTP CASE'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",article=article,old=template)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:article),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",article=article)
 meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:article;x.BARCODE_SHT:=:barcode;insert into RRL_ARTICULS values x;end;",old=article,article=article2,barcode="BC209B"+tag)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :article,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own209 second route point'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",article=article2,old=article)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:article),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",article=article2)
 q.execute("select count(*)from RRL_WARES where ID=:id",id=ware)
 if q.fetchone()[0]==0:
  meta("insert into RRL_WARES(ID,NAME,PREFIX,SPIS_OTBOR_ON_SCAN_OPALL)values(:ware,:name,:prefix,1)",ware=ware,name="Own209 isolated CASE "+tag,prefix="Q"+tag[:2])
  meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:ware,'BOTH',1)",ware=ware)
 for cell in(src,dst,dst2,"CPT_"+str(ware)):
  q.execute("select count(*)from RRL_CELLS where CELL=:id and WARE_ID=:ware",id=cell,ware=ware)
  if q.fetchone()[0]==0:
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM)values(:cell,:ware,0,0,0,:pick,:system)",cell=cell,ware=ware,pick=int(cell in(dst,dst2)),system=int(cell.startswith("CPT_")))
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 q.execute("select count(*)from RRL_PICK_FACE f join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=f.PICK_FACE_ID where f.WARE_ID=:ware and f.CELL_CODE=:cell and a.ARTICUL=:article",ware=ware,cell=dst,article=article)
 if q.fetchone()[0]==0:
  face=seq("RRL_PICK_FACE_SQ")
  meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY)values(:id,:ware,:cell,.2,'admin')",id=face,ware=ware,cell=dst)
  meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE)values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:article,.24,0,'FULL_PALLET')",face=face,article=article)
 meta("update RRL_PICK_FACE set PICK_SEQUENCE=1 where PICK_FACE_ID=:id",id=face)
 face2=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,PICK_SEQUENCE,MAX_VOLUME,CREATED_BY)values(:id,:ware,:cell,2,.2,'admin')",id=face2,ware=ware,cell=dst2)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE)values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:article,.24,0,'FULL_PALLET')",face=face2,article=article2)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 print("Fixture209",tag,"WARE",ware,"SKU",article,"revision",revision,flush=True)
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"2","expiry_date":"2030-01-01","price":0,"reason":"Own209 isolated real CASE API"},{"revision_id":revision})
  post("INVENTORY_REGISTER_LOT",{"uid":lot2,"cell":src,"article":article2,"quantity":"2","expiry_date":"2030-01-01","price":0,"reason":"Own209 second physical route point"},{"revision_id":revision})
  q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0];order=seq("RRL_CUSTOMER_ORDER_SQ")
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,:number,:customer,:ware)",id=order,number=lot,customer=customer,ware=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:order_id,1,:article,1,'EA')",order_id=order,article=article)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:order_id,2,:article,1,'EA')",order_id=order,article=article2)
  picking=PickingService();plan=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
  q.execute("select TASK_TYPE from RRL_PICK_TASK where PICK_PLAN_ID=:id",id=plan);assert q.fetchall()==[("CASE_PICK",),("CASE_PICK",)]
  wave=picking.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=ware,created_by="admin"))
  picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="QA209.LAUNCH:"+str(wave)))
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:id and STATUS not in('DONE','CANCELLED')",id=wave)
  for task,uid,from_cell,to_cell,qty in q.fetchall():
   post("TASK_COMPLETE",{"fact_qty":str(qty),"scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:id",id=wave)
  source_rows=q.fetchall();assert len(source_rows)==2
  q.execute("select l.CASE_PICK_LINE_ID,l.CELL_CODE,l.PICK_SEQUENCE,l.ARTICUL,t.CASE_PICK_TASK_ID,t.SSCC from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:id order by l.PICK_SEQUENCE",id=wave)
  first,second=q.fetchall();assert first[2]==1 and second[2]==2 and first[1]==dst and second[1]==dst2 and first[4]==second[4]
  line,cell,_,_,case,carrier=first;case,line=int(case),int(line)
  # Future slotting changes do not rewrite the issued route.
  meta("update RRL_PICK_FACE set PICK_SEQUENCE=99 where PICK_FACE_ID=:id",id=face)

  q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);case_type=q.fetchone()[0]
  tare_base="http://127.0.0.1:8088/api/inventory/tare"
  availability=api.get(tare_base+f"/warehouses/{ware}/availability");assert availability.status_code==200,availability.text[:1200]
  current=next(row for row in availability.json()if row["pallet_type_id"]==case_type)
  observed=api.post(tare_base+"/count",json={"operation_id":"QA209.TARE.COUNT:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,
      "condition":"GOOD","observed_quantity":"1","expected_version":current["balance_version"] or 0,
      "reason":"Own software fixture container observation, no hardware acceptance","decision_reference":"QA209:"+str(case)})
  assert observed.status_code==200,(observed.status_code,observed.text[:1300])
  booking="QA209.TARE.BOOK:"+str(case)
  booked=api.post(tare_base+"/book",json={"operation_id":booking,"place_kind":"CASE","place_id":str(case)})
  assert booked.status_code==200,(booked.status_code,booked.text[:1300])
  request(f"/tasks/{case}/claim",{});request(f"/tasks/{case}/start",{})
  operation="CASE.HTTP209:"+str(case)
  body={"operation_id":operation,"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article,"offline_event_id":operation}
  ahead={**body,"operation_id":"CASE209.AHEAD:"+str(case),"offline_event_id":"CASE209.AHEAD:"+str(case),"scan_cell":second[1],"scan_product":article2}
  rejected=api.post(base+f"/tasks/{case}/lines/{second[0]}/confirm",json=ahead)
  assert rejected.status_code==409 and "CASE_ROUTE_EARLIER_POINT_UNFINISHED"in rejected.text,(rejected.status_code,rejected.text[:1200])
  q.execute("select nvl(sum(PICKED_QTY),0)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id",id=case);assert q.fetchone()[0]==0
  result=request(f"/tasks/{case}/lines/{line}/confirm",body)
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);journal=q.fetchone();assert journal[0]>0
  assert request(f"/tasks/{case}/lines/{line}/confirm",body)==result
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);assert q.fetchone()==journal
  changed=api.post(base+f"/tasks/{case}/lines/{line}/confirm",json={**body,"fact_qty":"2"});assert changed.status_code==409
  ahead["operation_id"]="CASE209.SECOND:"+str(case);ahead["offline_event_id"]=ahead["operation_id"]
  second_result=request(f"/tasks/{case}/lines/{second[0]}/confirm",ahead)
  assert request(f"/tasks/{case}/lines/{second[0]}/confirm",ahead)==second_result
  q.execute("select nvl(sum(PICKED_QTY),0)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id",id=case);assert q.fetchone()[0]==2
  print("PASS209 distinct physical cells/frozen ranks1then2/futureface99 does not rewrite issued1/next point refused before first/native stock picks1+1/each replay",case,dst,dst2,flush=True)
  q.execute("select STATUS,CLOSED_AT,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);state=q.fetchone();assert state[0] in ("IN_PROGRESS","PICKED","PARTIAL")
  close_body={"operation_id":"CASE.CLOSE209.FIRST:"+str(case),"expected_content_version":int(state[2]),"reason":"Own209 actual picked place"}
  original=closing.record_close
  def fail_journal(*args,**kwargs):raise RuntimeError("Own209 after-state journal failure")
  closing.record_close=fail_journal
  try:
   try:close_existing_case_carrier(OracleGateway(),case,CaseCarrierCloseRequest(**close_body,actor="admin"),assert_case_task_access);raise AssertionError("Expected rollback")
   except RuntimeError as exc:assert "Own209 after-state"in str(exc)
  finally:closing.record_close=original
  q.execute("select STATUS,CLOSED_AT,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=case);assert q.fetchone()==state
  q.execute("select count(*)from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:id",id=close_body["operation_id"]);assert q.fetchone()[0]==0
  closed=request(f"/tasks/{case}/close-pallet",close_body);assert closed["status"]=="WAIT_CONTROL"and not closed["already_closed"]
  assert request(f"/tasks/{case}/close-pallet",close_body)==closed
  q.execute("select count(*)from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:id",id=close_body["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);assert q.fetchone()==(4,2)
  print("PASS209 actual HTTP CASE two units/journal snapshot unchanged on exactrepeat/changedbody409; real P4H2/firstcloseWAIT_CONTROL; after-state journalfailure rolls state+event back; close replay one event",flush=True)
 finally:
  if wave is not None:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:id",id=wave)
   for task,carrier,version in q.fetchall():
    q.execute("select h.LOT_UID,l.CELL_CODE from RRL_CASE_CARRIER_LOT h join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=h.CASE_PICK_LINE_ID where h.CASE_PICK_TASK_ID=:id and exists(select 1 from RRL_REMAINS r where r.UID_POLETA=h.LOT_UID and r.REMAIN>0)",id=task);destinations=dict(q.fetchall());lots=list(destinations)
    if lots:post("CASE_CARRIER_RETURN",{"destinations":destinations,"scan_container":carrier,"expected_content_version":int(version),"reason":"Own209 cleanup after preserved proof"},{"case_task_id":int(task)})
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:id and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",id=wave)
   for(reservation,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Own209 cleanup"},{"reservation_id":int(reservation)})
   try:post("WAVE_CANCEL",{"reason":"Own209 fixture retired after functional case"},{"document_type":"PICK_WAVE","document_id":wave})
   except oracledb.DatabaseError as exc:print("Own wave cancellation pending",str(exc.args[0]).split("\n",1)[0],flush=True)
  if booking is not None:
   cancelled=api.post(tare_base+"/book-cancel",json={"operation_id":"QA209.TARE.CANCEL:"+str(case),"booking_operation_id":booking})
   assert cancelled.status_code==200,(cancelled.status_code,cancelled.text[:1300])
   availability=api.get(tare_base+f"/warehouses/{ware}/availability")
   current=next(row for row in availability.json()if row["pallet_type_id"]==case_type)
   observed=api.post(tare_base+"/count",json={"operation_id":"QA209.TARE.ZERO:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,
       "condition":"GOOD","observed_quantity":"0","expected_version":current["balance_version"] or 0,
       "reason":"Retire owned empty software fixture container","decision_reference":"QA209.END:"+str(case)})
   assert observed.status_code==200,(observed.status_code,observed.text[:1300])
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION,p.ARTICUL from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL in(:article,:article2) and r.REMAIN>0",article=article,article2=article2)
  counts=[{"uid":uid,"cell":cell,"article":count_article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]}for uid,cell,unit,version,count_article in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End owned isolated one-unit CASE case","counts":counts},{"revision_id":revision})
  for plan in plans:meta("update RRL_PICK_RESERVATION set RESERVATION_STATUS='RELEASED'where PICK_PLAN_ID=:id and RESERVATION_STATUS='ACTIVE'",id=plan)
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=:ware",ware=ware);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own209 P/H cleared through native return/release/count; original135 P20H20 unchanged; history retained",flush=True)
