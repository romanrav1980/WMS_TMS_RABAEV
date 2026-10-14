import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import assign_sts
from app.modules.platform.public import read_oracle_json
from app.transport_composition import build_transport_loading
s=get_settings();tag="13508027ed";uid="RETURN237:"+tag;inn="9982370001";base="http://127.0.0.1:8088";h=httpx.Client(auth=("admin","admin123"),timeout=40)
def api(method,path,body=None,status=200):
 r=h.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:4000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select r.OPERATION_ID,r.WARE_ID,p.TARGET_CELL from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_PLACEMENT p on p.RECEIPT_OPERATION_ID=r.OPERATION_ID where r.PICKUP_OPERATION_ID=:p",p="RET237.PICKUP:"+tag);receipt,ware,cell=q.fetchone()
 def cfg(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select count(*)from RRL_SUPPLIERS where INN=:p",p=inn)
 if not q.fetchone()[0]:cfg("insert into RRL_SUPPLIERS(INN,NAME,SUPPLIER_GROUP)values(:p,'Own237 original marked supplier','OWN.QA')",p=inn)
 body={"operation_id":"RET237.SUP.PREP:"+tag,"receipt_operation_id":receipt,"supplier_inn":inn,"reason":"Own237 exact approved marked supplier return","decision_reference":"DEV.SUP237:"+tag}
 prepared=api("POST","/api/inventory/supplier-returns/prepare",body);assert api("POST","/api/inventory/supplier-returns/prepare",body)==prepared
 st=prepared["st_id"];identifier=prepared["shipment_identifier"];plate="QSUP237"+tag;dock="QD237"+tag
 q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:p",p=st);trip=q.fetchone()[0]
 if trip is None:
  q.execute("select ID from RRL_TR_VODITEL where F='Own237'and I='Supplier'and O='Driver'and nvl(DELETED,0)=0 order by ID");existing=q.fetchone()
  if existing:driver=existing[0]
  else:
   q.execute("select RRL_TR_VODITEL_SQ.nextval from dual");driver=q.fetchone()[0];cfg("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:p,'Own237','Supplier','Driver',0)",p=driver)
  q.execute("select ID from RRL_TR_VEHICLE where NUM=:p and nvl(DELETED,0)=0",p=plate);existing=q.fetchone()
  if existing:vehicle=existing[0]
  else:vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,"15",10,1,0,None]));c.commit()
  cfg("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:p",p=vehicle)
  cfg("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:p,:w,0)",p=dock,w=ware)
  q.execute("select RRL_TRANSPORT_TASK_SQ.nextval from dual");trip=int(q.fetchone()[0])
  cfg("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:p,:plate,'15','Спланирован',trunc(sysdate),:driver,:dock,0)",p=trip,plate=plate,driver=driver,dock=dock)
  assign_sts(OracleGateway(),trip,[prepared["st_number"]],"admin")
 loading=build_transport_loading();preview=loading.preview_single(identifier,"admin");assert preview["root"]==uid
 q.execute("select x.SYSTEM_CODE,x.PROFILES_JSON,x.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE x on x.UID_PALLET=u.UID_PALLET and x.UNIT_ID=u.UNIT_ID where u.CURRENT_UID=:p order by x.SYSTEM_CODE",p=uid);scans=[]
 for system,profiles,code in q.fetchall():
  for profile in read_oracle_json(profiles):scans.append({"system_code":system,"profile_code":profile["profile"],"code":code.read()if hasattr(code,"read")else code})
 qc=api("GET","/api/outgoing-quality/"+identifier)
 api("POST","/api/outgoing-quality/"+identifier+"/scan",{"operation_id":"RET237.SUP.QC:"+tag,"expected_composition_signature":qc["composition_signature"],"error_count":0,"scans":scans})
 preview=loading.preview_single(identifier,"admin")
 metadata={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":uid,"scan_cell":cell,"loading_context":{"transport_task_id":int(trip),"scan_vehicle":plate,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"2","width_m":"1","depth_m":"1","height_m":"1"}}}
 command={"contract_version":2,"operation_id":"RET237.SUP.LOAD:"+tag+".ROLLBACK","command_type":"LOAD_SHIPMENT","actor":"admin","source":{"pallet_identifier":identifier},"lines":[],"units":[],"metadata":metadata};out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  q.execute("select count(*)from RRL_EVENT_OUTBOX where CORRELATION_ID=:p and EVENT_TYPE='MARKED_SUPPLIER_RETURN_DISPATCHED'",p=command["operation_id"]);assert q.fetchone()[0]==2
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:x",p=uid,x=cell);assert q.fetchone()==(1,0)
 q.execute("select STOCK_STATUS,UNIT_VERSION from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p",p=uid);assert q.fetchone()==("AVAILABLE",12)
 loaded=loading.load_single("RET237.SUP.LOAD:"+tag,identifier,metadata,"admin");assert loading.load_single("RET237.SUP.LOAD:"+tag,identifier,metadata,"admin")==loaded
 departed=loading.depart("RET237.SUP.DEPART:"+tag,int(trip),"admin");assert departed["stock_consumed_again"]is False
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:x",p=uid,x=cell);assert q.fetchone()==(0,0)
 q.execute("select STOCK_STATUS,UNIT_VERSION,UID_PALLET from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p",p=uid);assert q.fetchone()==("ISSUED",13,"FULL.QA:"+tag)
 q.execute("select TARGET_SYSTEM,STATUS from RRL_EVENT_OUTBOX where CORRELATION_ID=:p and EVENT_TYPE='MARKED_SUPPLIER_RETURN_DISPATCHED'order by TARGET_SYSTEM",p="RET237.SUP.LOAD:"+tag);assert q.fetchall()==[("CRPT","PENDING"),("EGAIS","PENDING")]
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p",p="FULL.QA:"+tag);assert q.fetchone()[0]==6
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p="RET237.SUP.LOAD:"+tag);assert q.fetchone()[0]==1
 print("PASS237 existing supplier ST/QC2QR/native physical load-depart/exact1originalkey/P0H0/ISSUED13/same birth codes6/outer rollback including Gov queues/replay/CRPT-EGAIS PENDING notifications behind Regulatory API",prepared["st_id"],trip,identifier,flush=True)
