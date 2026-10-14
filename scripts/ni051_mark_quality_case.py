"""Actual full-pallet move -> existing ST binding -> pinned shipment; clean only own P/H through root."""
import json,sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
cfg=get_settings();tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="FULL.ST:"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**b):
  if ":ware" in sql:b["ware"]=ware
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):
  q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def post(kind,body,source,op=None):
  from app.modules.inventory.contracts_stock import StockCommand
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  if kind=="INVENTORY_REGISTER_LOT":
   body={**body,"birth_captures":{body["uid"]:{"units":codes_by_uid[body["uid"]],"aggregations":[]}}}
   return StockPosting().post(StockCommand(operation_id=op or "QM.BIRTH:"+uuid4().hex,command_type=kind,actor="admin",source=source,lines=(),metadata=body))
  if kind=="TASK_COMPLETE":
   from app.modules.inventory.infrastructure.task_scan_drafts import TaskScanDrafts
   from app.modules.inventory.infrastructure.task_completion import complete_existing_task
   from app.schemas import WarehouseTaskStatusRequest
   draft_service=TaskScanDrafts(OracleGateway());ctx=draft_service.context(source["task_id"])
   scans=[scan for unit in codes_by_uid[lot] for scan in unit["codes"]]
   request={"draft_id":"QM.DRAFT:"+uuid4().hex,"profile_signature":ctx["profile_signature"],"expected_stock_version":ctx["stock_version"],"scans":scans}
   draft_service.save(source["task_id"],request,"admin");draft=draft_service.latest(source["task_id"],"admin")
   return complete_existing_task(OracleGateway(),source["task_id"],WarehouseTaskStatusRequest(**body,operation_id=op or "QM.MOVE:"+uuid4().hex,scan_draft_id=request["draft_id"],unit_keys=draft["unit_keys"],updated_by="admin"),"admin")
  command={"contract_version":2,"operation_id":op or "FULL.QA:"+uuid4().hex,"command_type":kind,"actor":"admin","source":source,"lines":[],"units":[],"metadata":body}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=out.getvalue();conn.commit();return json.loads(result.read() if hasattr(result,"read") else result)
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");article=q.fetchone()[0]
 base_article=article;article="QMQC"+tag
 gtin_prefix="0460000000000";gtin=gtin_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1) for i,n in enumerate(reversed(gtin_prefix)))%10)%10)
 meta("declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;r.BARCODE_SHT:=:gtin;insert into RRL_ARTICULS values r;end;",old=base_article,a=article,gtin=gtin)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'QC marked own fixture' from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=base_article)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY) values(:a,1,1,'admin')",a=article)
 for system,profile in (("CRPT","TOBACCO"),("EGAIS","ALCOHOL")):
  meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE) values(:a,:s,:p,'QA1','UNIT')",a=article,s=system,p=profile)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 codes_by_uid={u:[{"unit_id":str(i),"codes":[{"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:4]+str(k)+str(i).zfill(2)},
  {"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(k)+str(i)).ljust(68,"X")}]} for i in range(3)] for k,u in enumerate((lot,other))}
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 ware=100000+int(tag[:6],16)
 meta("insert into RRL_WARES(ID,NAME,PREFIX,BLOCK_IF_NO_PROOVE) values(:ware,:n,:p,1)",n="QC private "+tag,p="Q"+tag[:2])
 for cell in (src,dst):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,:ware,0,0,0,0,0)",c=cell)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 order,row,plan,pl,pt,wave,wt,task,st,ff=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")]
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:ware)",id=order,no=lot,c=customer)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(:id,:o,1,:a,3,'EA')",id=row,o=order,a=article)
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS) values(:id,:o,:c,:ware,'RELEASED')",id=plan,o=order,c=customer)
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS) values(:id,:p,:r,:a,3,3,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
 meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY) values(:id,:p,:pl,:o,:c,'FULL_PALLET','NEW',:a,:u,:src,:dst,3)",id=pt,p=plan,pl=pl,o=order,c=customer,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:ware,'LAUNCHED','admin')",id=wave,code=lot)
 meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE) values(:id,:w,:p,'FULL_PALLET','NEW',:a,:u,3,:src,:dst)",id=wt,w=wave,p=pt,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY) values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:w,:u,:src,:dst,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=wt,w=wave,u=lot,src=src,dst=dst)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:u,:u,:ware,0,'Own full-pallet ST')",id=st,u=st_uid)
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',0.125)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 try:
  for u,cell in ((lot,src),(other,dst)):
   post("INVENTORY_REGISTER_LOT",{"uid":u,"cell":cell,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"Full-pallet binding fixture"},{"revision_id":revision})
   post("RESERVATION_CREATE",{"uid_pallet":u,"cell":cell,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  try:post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave});raise AssertionError("Unperformed wave closed")
  except oracledb.DatabaseError as exc:assert "WAVE_EXECUTION_OR_SHIPPING_PENDING" in str(exc),str(exc)
  before=OrderExecution(OracleGateway()).get(order);assert before["lines"][0]["picked_quantity"]=="0"
  try:post("PICK_PALLET_BIND_SHIPMENT",{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":0},{"task_id":task});raise AssertionError("Unperformed task bound")
  except oracledb.DatabaseError as exc:assert "FULLPAL_CONFIRMED_MOVE_REQUIRED" in str(exc),str(exc)
  completed=post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  assert preview["pallet_identifier"]==lot and preview["quantity"]=="3"
  body={"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])}
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Unbound physical pallet shipped")
  except oracledb.DatabaseError as exc:assert "FULLPAL_PHYSICAL_SHIPMENT_BIND_REQUIRED" in str(exc),str(exc)
  op="FULL.BIND:"+tag;bound=post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)
  assert post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)==bound
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff)
  assert q.fetchone()==("PICKED",3,"EA",task,lot)
  assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]=="3"
  meta("update RRL_SBORKA_PALLET_ROWS set EI='EA',QUANTITY=1 where PALLET_UID=:u",u=st_uid)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Bound whole pallet partially shipped after ST edit")
  except oracledb.DatabaseError as exc:assert "FULLPAL_BOUND_WHOLE_COMPOSITION_REQUIRED" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(3,3)
  meta("update RRL_SBORKA_PALLET_ROWS set EI='BOX',QUANTITY=0.125 where PALLET_UID=:u",u=st_uid)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Unchecked physical pallet shipped")
  except oracledb.DatabaseError as exc:assert "SHIPMENT_CURRENT_UNIQUE_MARK_CONTROL_REQUIRED" in str(exc),str(exc)
  meta("update RRL_WARES set BLOCK_IF_NO_PROOVE=0 where ID=:ware")
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Weight/control waiver bypassed unique marks")
  except oracledb.DatabaseError as exc:assert "SHIPMENT_CURRENT_UNIQUE_MARK_CONTROL_REQUIRED" in str(exc),str(exc)
  meta("update RRL_WARES set BLOCK_IF_NO_PROOVE=1 where ID=:ware")
  # Client supplied historical flags do not establish approval.
  meta("update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=1 where ID=:id",id=st)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Legacy flag bypassed composition gate")
  except oracledb.DatabaseError as exc:assert "SHIPMENT_CURRENT_UNIQUE_MARK_CONTROL_REQUIRED" in str(exc),str(exc)
  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  admission=OutgoingQuality(OracleGateway())
  status=admission.status(st_uid);assert status["required"] and not status["ready"] and len(status["composition_signature"])==64
  try:post("OUTGOING_PALLET_CHECK",{"quality_kind":"WEIGHT","gross_weight":"3","wood_weight":"0"},{"pallet_identifier":st_uid});raise AssertionError("Unknown SI mass policy approved")
  except oracledb.DatabaseError as exc:assert "QUALITY_SI_WEIGHT_POLICY_REQUIRED" in str(exc),str(exc)
  meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL) values(:ware,:a,:c)",a=article,c=dst)
  from app.modules.master_data.infrastructure.quality_weight_policy import QualityWeightPolicy
  from app.modules.master_data.api.quality_weight_routes import WeightPolicyInput
  mass=QualityWeightPolicy(OracleGateway())
  saved=mass.set(ware,article,WeightPolicyInput(base_uom="EA",expected_version=0,base_weight_kg="4",box_weight_kg="10"),"admin");assert saved["version"]==1
  try:mass.set(ware,article,WeightPolicyInput(base_uom="EA",expected_version=0,base_weight_kg="2",box_weight_kg="10"),"admin");raise AssertionError("Stale mass policy version overwritten")
  except Exception as exc:assert getattr(exc,"status_code",None)==409,str(exc)
  status=admission.status(st_uid)
  weight_only=post("OUTGOING_PALLET_CHECK",{"quality_kind":"WEIGHT","gross_weight":"12","wood_weight":"0"},{"pallet_identifier":st_uid});assert weight_only["verified"]==1 and not admission.status(st_uid)["ready"]
  quality={"quality_kind":"SCAN","error_count":0,"note":"Own QC composition case","expected_composition_signature":status["composition_signature"]}
  try:post("OUTGOING_PALLET_CHECK",{**quality,"expected_composition_signature":"0"*64},{"pallet_identifier":st_uid});raise AssertionError("Stale scanned composition approved")
  except oracledb.DatabaseError as exc:assert "QUALITY_SCANNED_COMPOSITION_CHANGED" in str(exc),str(exc)
  from app.modules.inventory.domain.mark_identity import canonical_mark
  from hashlib import sha256
  def proof(scans):
   return [{"system_code":x["system_code"],"profile_code":x["profile_code"],"code_hash":sha256(canonical_mark(x["system_code"],x["profile_code"],x["code"])["identity"].encode("utf-8")).hexdigest()} for x in scans]
  raw_scans=[x for unit in codes_by_uid[lot] for x in unit["codes"]]
  failed_proof=post("OUTGOING_PALLET_CHECK",quality,{"pallet_identifier":st_uid})
  assert failed_proof["verified"]==0 and failed_proof["shipped"]==0 and failed_proof["failure_reason"]=="QUALITY_UNIQUE_UNIT_PROFILE_COVERAGE_REQUIRED",failed_proof
  assert not admission.status(st_uid)["ready"] and admission.status(st_uid)["rescan_required"]
  failed_proof=post("OUTGOING_PALLET_CHECK",{**quality,"unit_scans":proof(raw_scans[:-1])},{"pallet_identifier":st_uid})
  assert failed_proof["verified"]==0 and failed_proof["shipped"]==0 and failed_proof["failure_reason"]=="QUALITY_UNIQUE_UNIT_PROFILE_COVERAGE_REQUIRED",failed_proof
  assert not admission.status(st_uid)["ready"] and admission.status(st_uid)["rescan_required"]
  failed_proof=post("OUTGOING_PALLET_CHECK",{**quality,"unit_scans":proof(raw_scans+[codes_by_uid[other][0]["codes"][0]])},{"pallet_identifier":st_uid})
  assert failed_proof["verified"]==0 and failed_proof["shipped"]==0 and failed_proof["failure_reason"]=="QUALITY_FOREIGN_UNIT_OR_PROFILE",failed_proof
  assert not admission.status(st_uid)["ready"] and admission.status(st_uid)["rescan_required"]
  failed_proof=post("OUTGOING_PALLET_CHECK",{**quality,"unit_scans":proof(raw_scans+[raw_scans[0]])},{"pallet_identifier":st_uid})
  assert failed_proof["verified"]==0 and failed_proof["shipped"]==0 and failed_proof["failure_reason"]=="QUALITY_DUPLICATE_MARK_SCAN",failed_proof
  assert not admission.status(st_uid)["ready"] and admission.status(st_uid)["rescan_required"]
  # The authenticated API adapter hashes actual raw QR, root still verifies its registry binding.
  api_qc=admission.check(st_uid,{**quality,"operation_id":"QM.API:"+tag,"scans":raw_scans},"admin");assert api_qc["verified"]==1
  quality["unit_scans"]=proof(raw_scans)
  qcop="QC.SCAN:"+tag
  qc=post("OUTGOING_PALLET_CHECK",quality,{"pallet_identifier":st_uid},qcop)
  assert qc["verified"]==1 and qc["shipped"]==0
  assert post("OUTGOING_PALLET_CHECK",quality,{"pallet_identifier":st_uid},qcop)==qc
  q.execute("select SCAN_CONTENT_SIGNATURE,SCAN_QC_OPERATION_ID from RRL_SBORKA_PALLETS where ID=:id",id=st)
  signature,recorded_op=q.fetchone();assert len(signature)==64 and recorded_op==qcop
  assert admission.status(st_uid)["ready"]
  q.execute("select SCAN_MARK_PROVED,SCAN_PHYSICAL_UNIT_COUNT from RRL_SBORKA_PALLETS where ID=:id",id=st);assert q.fetchone()==(1,3)
  from decimal import Decimal
  expected,tolerance=Decimal("12"),Decimal("5")
  assert tolerance>0
  weight={**quality,"quality_kind":"WEIGHT","gross_weight":str(expected+tolerance),"wood_weight":"0"}
  weighed=post("OUTGOING_PALLET_CHECK",weight,{"pallet_identifier":st_uid});assert weighed["verified"]==1 and admission.status(st_uid)["ready"]
  assert admission.status(st_uid)["weight_matches"]
  lower=post("OUTGOING_PALLET_CHECK",{**weight,"gross_weight":str(expected-tolerance)},{"pallet_identifier":st_uid});assert lower["verified"]==1
  below=post("OUTGOING_PALLET_CHECK",{**weight,"gross_weight":str(expected-tolerance-Decimal("0.000000001"))},{"pallet_identifier":st_uid});assert below["verified"]==0 and not admission.status(st_uid)["ready"]
  post("OUTGOING_PALLET_CHECK",weight,{"pallet_identifier":st_uid})
  mass.set(ware,article,WeightPolicyInput(base_uom="EA",expected_version=1,base_weight_kg="2",box_weight_kg="10"),"admin")
  assert not admission.status(st_uid)["ready"]
  mass.set(ware,article,WeightPolicyInput(base_uom="EA",expected_version=2,base_weight_kg="4",box_weight_kg="10"),"admin")
  assert not admission.status(st_uid)["ready"]
  quality["expected_composition_signature"]=admission.status(st_uid)["composition_signature"]
  weight["expected_composition_signature"]=quality["expected_composition_signature"]
  post("OUTGOING_PALLET_CHECK",weight,{"pallet_identifier":st_uid})
  failed=post("OUTGOING_PALLET_CHECK",{**weight,"gross_weight":str(expected+tolerance+Decimal("0.000000001"))},{"pallet_identifier":st_uid})
  assert failed["verified"]==0 and not admission.status(st_uid)["ready"]
  post("OUTGOING_PALLET_CHECK",quality,{"pallet_identifier":st_uid})

  meta("update RRL_SBORKA_PALLET_ROWS set QUANTITY=0.25 where PALLET_UID=:u",u=st_uid)
  try:post("OUTGOING_PALLET_CHECK",quality,{"pallet_identifier":st_uid});raise AssertionError("Mismatched physical composition approved")
  except oracledb.DatabaseError as exc:assert "SHIPMENT_OWN_PICKED_RESERVATION_INSUFFICIENT" in str(exc),str(exc)
  meta("update RRL_SBORKA_PALLET_ROWS set QUANTITY=0.125 where PALLET_UID=:u",u=st_uid)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Edited then restored row resurrected approval")
  except oracledb.DatabaseError as exc:assert "SHIPMENT_CURRENT_UNIQUE_MARK_CONTROL_REQUIRED" in str(exc),str(exc)
  post("OUTGOING_PALLET_CHECK",quality,{"pallet_identifier":st_uid})
  shipop="FULL.SHIP:"+tag;shipped=post("SHIP_PALLET",{},{"pallet_identifier":st_uid},shipop)
  assert post("SHIP_PALLET",{},{"pallet_identifier":st_uid},shipop)==shipped
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(0,0)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(3,3)
  q.execute("select STATUS,FACT_QTY,FACT_UOM,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff);assert q.fetchone()==("SHIPPED",3,"EA",shipop)
  from app.modules.inventory.infrastructure.wave_execution import WaveExecution
  lifecycle=WaveExecution(OracleGateway())
  waiting=lifecycle.preview(wave, "admin");assert not waiting["ready"] and any(x["reason"]=="ACTIVE_WAVE_HARD_REMAINS" for x in waiting["items"])
  try:post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave});raise AssertionError("Wave with active HARD closed")
  except oracledb.DatabaseError as exc:assert "WAVE_EXECUTION_OR_SHIPPING_PENDING" in str(exc),str(exc)
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and SOURCE_DOC_ID=:w and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",u=other,w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Release separate fixture owner after preserved-stock proof"},{"reservation_id":int(rid)})
  assert lifecycle.preview(wave, "admin")["ready"]
  finishop="WAVE.FINISH:"+tag
  finished=post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave},finishop);assert finished["completed"] and finished["status"]=="DONE"
  assert post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave},finishop)==finished
  print("PASS unique marked QC: physical3 with CRPT+EGAIS6 codes; count-only/missing profile/foreign/duplicate deny; raw-code API proof and replay",flush=True)
  print("PASS required QC: legacy flag denied, exact scan/replay, mismatched quantity denied, edit/restore requires new approval",flush=True)
  print("PASS root wave finish denied before physical execution and while own HARD remains; shipped facts + no HARD -> DONE/replay",flush=True)
  print("PASS actual full pallet3 -> ST0.125BOX binding + BASE3/provenance/replay -> pinned shipment consumes this pallet only, other owned pallet remains3",flush=True)
 finally:
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End private full-pallet fixture"},{"reservation_id":int(rid)})
  q.execute("select UID_POLETA,CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA in(:a,:b) and REMAIN>0",a=lot,b=other)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  for count in counts:
   q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE' order by PHYSICAL_UNIT_KEY",u=count["uid"],c=count["cell"]);count["unit_keys"]=[k for (k,) in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End private full-pallet fixture","counts":counts},{"revision_id":revision})
  meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:id and STATUS!='DONE'",id=task)
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H restored; immutable operation and fulfillment history retained",flush=True)
