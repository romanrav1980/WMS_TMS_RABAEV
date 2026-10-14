exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from app.modules.platform.public import read_oracle_json
from app.modules.transport.public import assign_sts
from app.oracle_gateway import OracleGateway
from app.transport_composition import build_transport_loading
p=Path("tmp/context483.json");saved=json.loads(p.read_text(encoding="utf-8"));part=saved["REFUSED"];tag=saved["tag"];ware=38542432
uid=part["receipt"]["pallet_identifier"];cell=part["placement"]["to_cell"];inn="9984910001";plate="QS491"+tag;dock="QD491"+tag
base="http://127.0.0.1:8088";h=httpx.Client(auth=("admin","admin123"),timeout=40)
def api(method,path,body=None,status=200):
 r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def cfg(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select count(*)from RRL_SUPPLIERS where INN=:inn",inn=inn)
 if q.fetchone()[0]==0:cfg("insert into RRL_SUPPLIERS(INN,NAME,SUPPLIER_GROUP)values(:inn,'Own491 unaccepted delivery goods supplier','OWN.QA')",inn=inn)
 if "supplier_prepared"not in part:
  body=dict(operation_id="EXRET491.SUP.PREP:"+tag,receipt_operation_id=part["receipt"]["operation_id"],supplier_inn=inn,reason="Refused-at-delivery unit returned to supplier",decision_reference="DEV491:"+tag)
  part["supplier_prepared"]=api("POST","/api/inventory/supplier-returns/prepare",body);part["supplier_prepared_body"]=body;save()
 prepared=part["supplier_prepared"];st=prepared["st_id"];identifier=prepared["shipment_identifier"]
 if "supplier_trip"not in part:
  q.execute("select RRL_TR_VODITEL_SQ.nextval from dual");driver=int(q.fetchone()[0])
  cfg("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:id,'Own491','Supplier','Driver',0)",id=driver)
  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,"15",10,1,0,None]));c.commit()
  cfg("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
  cfg("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock,ware=ware)
  q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=int(q.fetchone()[0])
  cfg("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,'15','Спланирован',trunc(sysdate),:driver,:dock,0)",id=trip,plate=plate,driver=driver,dock=dock)
  assign_sts(OracleGateway(),trip,[prepared["st_number"]],"admin")
  part["supplier_trip"]=trip;save()
 trip=part["supplier_trip"];loading=build_transport_loading()
 if "supplier_load"not in part:
  q.execute("select UNIT_VERSION,UID_PALLET from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:k",k=saved["selected"]["REFUSED"][0]);version,origin=q.fetchone()
  qc=api("GET","/api/outgoing-quality/"+identifier)
  api("POST","/api/outgoing-quality/"+identifier+"/scan",dict(operation_id="EXRET491.QC:"+tag,expected_composition_signature=qc["composition_signature"],error_count=0,scans=part["receipt_body"]["scans"]))
  preview=loading.preview_single(identifier,"admin");assert preview["root"]==uid,preview
  metadata=dict(expected_version=preview["expected_version"],expected_composition_signature=preview["composition_signature"],scan_container=uid,scan_cell=cell,loading_context=dict(transport_task_id=trip,scan_vehicle=plate,scan_dock=dock,measurements=dict(origin="MANUAL_CONFIRMED",content_version=preview["expected_version"],gross_weight_kg="0.25",width_m="0.25",depth_m="0.25",height_m="0.25")))
  operation="EXRET491.LOAD:"+tag
  command=dict(contract_version=2,operation_id=operation+".ROLLBACK",command_type="LOAD_SHIPMENT",actor="admin",source=dict(pallet_identifier=identifier),lines=[],units=[],metadata=metadata)
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=cell);assert q.fetchone()==(0,0)
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=cell);assert q.fetchone()==(1,0)
  part["supplier_load"]=loading.load_single(operation,identifier,metadata,"admin");part["supplier_load_body"]=metadata;part["supplier_load_operation"]=operation;save()
 assert loading.load_single(part["supplier_load_operation"],identifier,part["supplier_load_body"],"admin")==part["supplier_load"]
 if "supplier_departure"not in part:
  part["supplier_departure"]=loading.depart("EXRET491.DEPART:"+tag,trip,"admin");save()
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=uid,cell=cell);assert q.fetchone()==(0,0)
 q.execute("select STOCK_STATUS from RRL_WMS_RECEIPT_UNIT where PHYSICAL_UNIT_KEY=:k",k=saved["selected"]["REFUSED"][0]);assert q.fetchone()[0]=="ISSUED"
 q.execute("select TARGET_SYSTEM,STATUS from RRL_EVENT_OUTBOX where CORRELATION_ID=:op and EVENT_TYPE='MARKED_SUPPLIER_RETURN_DISPATCHED'order by TARGET_SYSTEM",op=part["supplier_load_operation"]);assert q.fetchall()==[("CRPT","PENDING"),("EGAIS","PENDING")]
 q.execute("select ACCEPTED_BASE_QTY,MISSING_BASE_QTY,REFUSED_BASE_QTY,DAMAGED_BASE_QTY from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op",op=saved["receipt"]);assert q.fetchone()==(3,2,1,1)
 saved["result"]="REFUSED1_SUPPLIER_DEPARTED_DAMAGED1_DISPOSED_BUYER3_UNCHANGED";save()
 print("PASS491 refused1 supplier existing PALL_SPLITTER/ST/assignment/QC2/nativeLOAD/DEPART/P0/same originalkey/rollback-replay/two pending regulatory messages; buyerAccepted3 and missing2 preserved")
