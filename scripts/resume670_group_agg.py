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
cfg=get_settings()
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
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=out.getvalue();conn.commit();return json.loads(result.read() if hasattr(result,"read") else result)
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 ctx=json.loads(Path("tmp/source670_progress.json").read_text(encoding="utf-8"))
 globals().update(ctx);ware=ctx["warehouse"];gtin=ctx["barcode"];receive="QR670"+tag;pick="QK670"+tag
 import httpx
 from app.modules.platform.public import read_oracle_json
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(method,path,body=None,status=200):
  r=admin_api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
 q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE='APPLIED'",op="IW670.BIRTH:"+tag);born=read_oracle_json(q.fetchone()[0])
 # A private equal-distance fixture selected another empty storage cell correctly.
 # Give this SKU's private pick face and intended storage a distinct coordinate, then use existing replan.
 for cell in(src,pick):meta("update RRL_CELLS set X=100 where CELL=:cell and WARE_ID=:ware",cell=cell)
 replanned=api("POST","/api/receiving/putaway/"+str(born["task_id"])+"/replan",dict(operation_id="IW670.REPLAN:"+tag,scanned_pallet=lot,scanned_from_cell=receive,reason="Private SKU pick-face coordinates; nearest free storage"))
 assert replanned["placement"]["cell"]==src,replanned
 try:
  api("POST","/api/receiving/putaway/"+str(born["task_id"])+"/complete",dict(scanned_pallet=lot,scanned_from_cell=receive,scanned_to_cell=src))

  post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  before=OrderExecution(OracleGateway()).get(order);assert before["lines"][0]["picked_quantity"]=="0"
  completed=post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  assert preview["pallet_identifier"]==lot and preview["quantity"]=="3"
  body={"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])}
  op="FULL.BIND:"+tag;bound=post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)
  assert post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)==bound
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff)
  assert q.fetchone()==("PICKED",3,"EA",task,lot)
  assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]=="3"
  post("INTERNAL_MOVE",{"uid":lot,"source_cell":dst,"target_cell":shipcell,"quantity":"0","unit":"EA"},{})
  from app.transport_composition import build_transport_loading
  loading=build_transport_loading();preview=loading.preview_single(st_uid)
  assert preview["root"]==lot and preview["snapshot"]["nodes"][0]["kind"]=="STOCK"
  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  qc=OutgoingQuality(OracleGateway());quality=qc.status(st_uid,"admin")
  scans=[code for unit in units for code in unit["codes"]]
  api("POST","/api/outgoing-quality/"+st_uid+"/scan",{"operation_id":"IW670.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
  assert qc.status(st_uid,"admin")["ready"]
  context=dict(tag=tag,article=article,lot=lot,warehouse=ware,shipcell=shipcell,src=src,dst=dst,task=task,st=st,st_uid=st_uid,order=order,wave=wave,vehicle=vehicle,dock=dock,source_trip=trip,barcode=gtin,units=units,ff=ff,driver=driver,trtype=trtype)
  Path("tmp/context670.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
  print("SOURCE_670 picked3/QC/currentP3H3; not loaded, group preparation next")
 finally:
  conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")

