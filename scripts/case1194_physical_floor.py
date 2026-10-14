"""One fresh thermal loading case through real root; retain receipt for continuation, never rerun factory."""
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
context_path=Path("tmp/context1194.json");assert not context_path.exists(),"Retained fixture; continue from context, do not recreate"
cfg=get_settings();tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="FULL.ST:"+tag
context={"tag":tag,"lot":lot,"state":"BUILDING"};context_path.write_text(json.dumps(context),encoding="utf-8")
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
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 ware=100000+int(tag[:6],16);context['warehouse_id']=ware;context_path.write_text(json.dumps(context),encoding='utf-8');shipcell="QH"+tag;top="HU.FULL:"+tag;box="HU.FULL.BOX:"+tag
 meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:ware,:n,:p)",n="Own FULLPAL HU "+tag,p="Q"+tag[:2])
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT) values(:ware,'NONE',0)")
 for cell in (src,dst,shipcell):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,0,0,0)",c=cell)
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
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'EA',3)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 q.execute("select min(TRANSPORTTYPE) from RRL_TRANSPORT_TYPE");trtype=q.fetchone()[0]
 q.execute("select min(ID) from RRL_TR_VODITEL where ID>0 and nvl(DELETED,0)=0");driver=q.fetchone()[0];assert driver
 vehicle=10100
 q.execute("select NUM,TR_TYPE from RRL_TR_VEHICLE where ID=:id",id=vehicle);vehicle_plate,trtype=q.fetchone()
 trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag
 meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED) values(:dock,:ware,0)",dock=dock)
 meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED) values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",id=trip,plate=vehicle_plate,typ=trtype,driver=driver,dock=dock)
 meta("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
 meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:tt where ID=:id",tt=trip,id=st)

 context.update({"article":article,"order_id":order,"task_id":task,"st_id":st,"st_identifier":st_uid,"vehicle_id":vehicle,"trip_id":trip,"dock":dock,"ship_cell":shipcell,"source_cell":src,"target_cell":dst})
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"Own1194 physical top tare case"},{"revision_id":revision})
 post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
 post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
 post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
 preview=FullPalletShipment(OracleGateway()).preview(task)
 post("PICK_PALLET_BIND_SHIPMENT",{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])},{"task_id":task})
 post("INTERNAL_MOVE",{"uid":lot,"source_cell":dst,"target_cell":shipcell,"quantity":"0","unit":"EA"},{})
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:ware,:a,:cell,2,6)",a=article,cell=dst)
 from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
 from app.transport_composition import build_transport_loading
 hu=WarehouseHu(OracleGateway());loading=build_transport_loading()
 context.update(state="READY_TO_ASSEMBLE",top=top,vehicle_plate=vehicle_plate);context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 hu.command("HU_CREATE",top,"FLOOR1194.CREATE:"+tag,{"cell":shipcell,"warehouse":ware,"container_type":"PALLET","tare_weight_kg":"1","scan_container":top,"scan_cell":shipcell},"admin")
 outer=hu.preview(top,"admin");leaf=hu.preview(lot,"admin")
 hu.command("HU_ATTACH",top,"FLOOR1194.ATTACH:"+tag,{"child_uid":lot,"expected_version":outer["nodes"][0]["version"],"expected_child_version":leaf["nodes"][0]["version"],"scan_container":top,"scan_child":lot},"admin")
 post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own1194 software dev tare opening","decision_reference":"DEV1194:"+tag},{},"FLOOR1194.COUNT:"+tag)
 post("TARE_BOOK",{"pallet_type_id":1},{"place_kind":"HU","place_id":top},"FLOOR1194.BOOK:"+tag)
 tree=hu.preview(top,"admin");assert tree["top_place_count"]==1 and len(tree["nodes"])==2
 body={"expected_version":tree["nodes"][0]["version"],"scan_container":top,"scan_cell":shipcell,
       "loading_context":{"transport_task_id":trip,"scan_vehicle":vehicle_plate,"scan_dock":dock,
        "measurements":{"origin":"MANUAL_CONFIRMED","content_version":tree["nodes"][0]["version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"},
        "temperature_confirmation":{"origin":"MANUAL_AT_LOADING","observed_c":"3.125","vehicle_profile_version":2,"observation_reference":"DEV1194.TEMP:"+tag}}}
 trial="FLOOR1194.ROLLBACK:"+tag
 command={"contract_version":2,"operation_id":trial,"command_type":"HU_SHIP","actor":"admin","source":{"uid":top},"lines":[],"units":[],"metadata":body}
 context.update(state="READY_TO_LOAD",body=body,tree=tree,trial_operation=trial,load_operation="FLOOR1194.LOAD:"+tag)
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=trial)
  assert q.fetchone()==(1,"HELD_HU_TARE_BOOK")
 finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select count(*)from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=trial);assert q.fetchone()==(0,)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(3,3)
 result=loading.load(context["load_operation"],top,body,"admin")
 assert loading.load(context["load_operation"],top,body,"admin")==result
 q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN,PROFILE_VERSION from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=context["load_operation"]);assert q.fetchone()==(1,"HELD_HU_TARE_BOOK",2)
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot",lot=lot);assert q.fetchone()==(0,0)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cl on cl.CELL=r.CELL where cl.WARE_ID=5062399");assert q.fetchone()==(20,20)
 context.update(state="LOADED",result=result,protected_stock=[20,20])
 context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
 print(json.dumps({"case":"PASS1194","trip":trip,"vehicle":vehicle,"top_type":1,"top_count":1,"nodes":2,"stock":[0,0],"protected":[20,20]}))
