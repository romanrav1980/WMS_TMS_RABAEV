exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service,StockCommand
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
from app.modules.transport.public import create_existing_trip,update_existing_trip,assign_sts
from datetime import datetime,timedelta,timezone,date
import httpx
ret=json.loads(Path("tmp/context394.json").read_text());old=ret["source"]["source"];tag=old["tag"];ware=old["warehouse"];lot=ret["returned_uid"];article=old["article"];src=old["pick"];dst="QG396"+tag;shipcell="QH396"+tag;dock="QD396"+tag
p=Path("tmp/context396.json")
if p.exists():raise SystemExit("Re-shipment396 already created; resume retained source")
progress=Path("tmp/progress396.json");saved=json.loads(progress.read_text())if progress.exists()else{}
def save():progress.write_text(json.dumps(saved,indent=2),encoding="utf-8")
posting=build_stock_posting_service();gw=OracleGateway();loading=build_transport_loading()
def post(kind,source,meta,op):return posting.post(StockCommand(operation_id=op,command_type=kind,actor="admin",source=source,metadata=meta,lines=()))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 if "metadata"not in saved:
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:
   for cell in[dst,shipcell]:
    q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,0,0,0,0)",cell=cell,ware=ware)
    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
   q.execute("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock,ware=ware)
   q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0]
   order,row,plan,pl,pt,wave,wt,task,st,ff=[seq(n)for n in("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")]
   st_uid="RS396:"+tag
   q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,:no,:customer,:ware)",id=order,no="RS396:"+tag,customer=customer,ware=ware)
   q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(:id,:order_id,1,:article,2,'EA')",id=row,order_id=order,article=article)
   q.execute("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS)values(:id,:order_id,:customer,:ware,'RELEASED')",id=plan,order_id=order,customer=customer,ware=ware)
   q.execute("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS)values(:id,:plan,:row_id,:article,2,2,'PLANNED_FULL')",id=pl,plan=plan,row_id=row,article=article)
   q.execute("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY)values(:id,:plan,:pl,:order_id,:customer,'FULL_PALLET','NEW',:article,:lot,:src,:dst,2)",id=pt,plan=plan,pl=pl,order_id=order,customer=customer,article=article,lot=lot,src=src,dst=dst)
   q.execute("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY)values(:id,:code,:ware,'LAUNCHED','admin')",id=wave,code="RS396:"+tag,ware=ware)
   q.execute("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE)values(:id,:wave,:pt,'FULL_PALLET','NEW',:article,:lot,2,:src,:dst)",id=wt,wave=wave,pt=pt,article=article,lot=lot,src=src,dst=dst)
   q.execute("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY)values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:wave,:lot,:src,:dst,:ware,:ware,2,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=wt,wave=wave,lot=lot,src=src,dst=dst,ware=ware)
   q.execute("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:id,:st,:st,:ware,0,'Own full-pallet ST')",id=st,st=st_uid,ware=ware)
   q.execute("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:st,:article,'BOX',2)",st=st_uid,article=article)
   q.execute("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(:id,:order_id,:st,:identifier,'PLANNED',0)",id=ff,order_id=order,st=st,identifier=st_uid)
   c.commit();saved.update(metadata=True,order=order,plan=plan,pl=pl,pt=pt,wave=wave,task=task,st=st,st_uid=st_uid,ff=ff,customer=customer);save()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 if "source_trip"not in saved:
  saved["source_trip"]=create_existing_trip(gw,"15",date(2026,10,12),"admin");save()
  update_existing_trip(gw,saved["source_trip"],dict(transport=old["plate"],transtype="15",dock=dock,voditel_id=old["driver"]),"admin")
  assign_sts(gw,saved["source_trip"],[saved["st_uid"]],"admin");saved["assigned"]=True;save()
 if "reserved"not in saved:
  saved["reserved"]=post("RESERVATION_CREATE",dict(type="PICK_WAVE",id=saved["wave"]),dict(uid_pallet=lot,cell=src,articul=article,qty="2",unit_code="EA",ware_id=ware,reservation_kind="HARD",reservation_scope="PALLET",reservation_domain="PICKING",source_doc_type="PICK_WAVE",source_doc_id=saved["wave"],source_line_id=saved["pt"],customer_order_id=saved["order"],customer_id=saved["customer"],pick_plan_id=saved["plan"],pick_plan_line_id=saved["pl"]),"IW396.RESERVE:"+tag);save()
 if "released"not in saved:saved["released"]=post("WAVE_PICK_RELEASE",dict(wave_id=saved["wave"]),{},"IW396.RELEASE:"+tag);save()
 if "moved"not in saved:saved["moved"]=post("TASK_COMPLETE",dict(task_id=saved["task"]),dict(fact_qty="2",scanned_pallet=lot,scanned_from_cell=src,scanned_to_cell=dst),"IW396.PICK:"+tag);save()
 if "bound"not in saved:
  view=FullPalletShipment(gw).preview(saved["task"])
  saved["bound"]=FullPalletShipment(gw).bind(saved["task"],dict(operation_id="IW396.BIND:"+tag,shipment_identifier=saved["st_uid"],scanned_pallet=lot,expected_stock_version=view["stock_version"]),"admin");save()
 if "to_shipping"not in saved:saved["to_shipping"]=post("INTERNAL_MOVE",{},dict(uid=lot,source_cell=dst,target_cell=shipcell,quantity="0",unit="EA"),"IW396.TOSHIP:"+tag);save()
 with httpx.Client(auth=("admin","admin123"),timeout=40)as h:
  if "qc"not in saved:
   r=h.get("http://127.0.0.1:8088/api/outgoing-quality/"+saved["st_uid"]);assert r.status_code==200,r.text
   r=h.post("http://127.0.0.1:8088/api/outgoing-quality/"+saved["st_uid"]+"/scan",json=dict(operation_id="IW396.QC:"+tag,expected_composition_signature=r.json()["composition_signature"],error_count=0,scans=[code for unit in old["units"]for code in unit["codes"]]));assert r.status_code==200,r.text;saved["qc"]=r.json();save()
 if "loaded"not in saved:
  preview=loading.preview_single(saved["st_uid"])
  meta=dict(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"],scan_container=lot,scan_cell=shipcell,loading_context=dict(transport_task_id=saved["source_trip"],scan_vehicle=old["plate"],scan_dock=dock,measurements=dict(origin="MANUAL_CONFIRMED",content_version=preview["expected_version"],gross_weight_kg="3",width_m="1",depth_m="1",height_m="1.5")))
  op="IW396.LOAD:"+tag;saved["loaded"]=loading.load_single(op,saved["st_uid"],meta,"admin");saved["source_load"]=op;save()
 if "departed"not in saved:saved["departed"]=loading.depart("IW396.DEPART:"+tag,saved["source_trip"],"admin");save()
 target=json.loads(Path("tmp/context390.json").read_text())["warehouse"];inbound="QI396"+tag;outbound="QO396"+tag
 if "target_trip"not in saved:
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:
   for dc in[inbound,outbound]:q.execute("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dc,:ware,0)",dc=dc,ware=target)
   c.commit()
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
  saved["target_trip"]=create_existing_trip(gw,"15",date(2026,10,12),"admin");save()
  update_existing_trip(gw,saved["target_trip"],dict(transport=old["plate"],transtype="15",dock=outbound,voditel_id=old["driver"]),"admin")
 now=datetime.now(timezone.utc);op="IW396.PLAN:"+tag
 if "plan_result"not in saved:saved["plan_result"]=Interwarehouse(gw,posting).plan(op,saved["source_load"],target,saved["target_trip"],inbound,now+timedelta(hours=1),now+timedelta(hours=2),"Actual returned original units shipped on a new order","DEV396:"+tag,"admin");save()
 context={**old,**saved,"lot":lot,"warehouse":ware,"target_warehouse":target,"inbound":inbound,"outbound":outbound,"plan_operation_id":op,"source_quantity":"2","source_load":saved["source_load"],"old_birth_uid":json.loads(Path("tmp/context390.json").read_text())["lot"]}
 p.write_text(json.dumps(context,indent=2),encoding="utf-8")
print("SOURCE396 actual returned two oldkeys/fourQR/reserved-moved-bound-originalST/neworder2/QC/load/depart/newfirstlegplan/no new birth")
