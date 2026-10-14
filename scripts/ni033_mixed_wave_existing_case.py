"""172 prepared own metadata403; native full3 QC/shipment + empty1 cancel + mixed finish."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.modules.master_data.infrastructure.quality_weight_policy import QualityWeightPolicy
from app.modules.master_data.contracts_quality_weight import WeightPolicyInput
f=json.loads(Path("tmp/ni033_mixed172_fixture.json").read_text(encoding="utf-8-sig"));s=get_settings();posting=StockPosting();base="http://127.0.0.1:8088/api"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c,httpx.Client(auth=("admin","admin123"),timeout=60)as client:
 q=c.cursor()
 def posted(op):
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=op);return q.fetchone()[0]>0
 def post(kind,source,metadata,op,actor="admin"):
  return posting.post(StockCommand(operation_id=op,command_type=kind,actor=actor,source=source,metadata=metadata,lines=()))
 def api(path,body):
  r=client.post(base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
 try:
  for key,quantity,uid,cell in[("full","3",f["full_uid"],f["source_cell"]),("empty","2",f["case_uid"],f["case_cell"])]:
   post("INVENTORY_REGISTER_LOT",{"revision_id":f["revision"]},{"uid":uid,"cell":cell,"article":f["article"],"quantity":quantity,"expiry_date":"2030-01-01","price":0,"reason":"Owned172 synthetic mixed wave fixture"},"MIXED172.REG:"+key)
   plan=f[key]
   post("RESERVATION_CREATE",{},{"reservation_kind":"HARD","reservation_scope":"PALLET"if key=="full"else"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":f["wave"],"source_line_id":plan["pt"],"uid_pallet":uid,"cell":cell,"articul":f["article"],"ware_id":f["ware"],"unit_code":"EA","qty":"3"if key=="full"else"1","customer_order_id":plan["order"],"pick_plan_id":plan["plan"],"pick_plan_line_id":plan["line"]},"MIXED172.HARD:"+key)
  post("WAVE_PICK_RELEASE",{"wave_id":f["wave"]},{},"MIXED172.PICK_RELEASE")
  post("TASK_COMPLETE",{"task_id":f["task"]},{"fact_qty":"3","scanned_pallet":f["full_uid"],"scanned_from_cell":f["source_cell"],"scanned_to_cell":f["target_cell"]},"MIXED172.FULL_PICK")
  shipping=FullPalletShipment(OracleGateway())
  q.execute("select PICKED_WAREHOUSE_TASK_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:p_ff",p_ff=f["ff"]);bound=q.fetchone()[0]
  if bound is None:
   preview=shipping.preview(f["task"])
   shipping.bind(f["task"],{"operation_id":"MIXED172.BIND","shipment_identifier":f["shipment"],"scanned_pallet":f["full_uid"],"expected_stock_version":int(preview["stock_version"])},"admin")
  q.execute("select count(*)from RRL_RECEIPT_SKU_RULE where WARE_ID=:p_ware and ARTICUL=:p_article",p_ware=f["ware"],p_article=f["article"])
  if q.fetchone()[0]==0:
   from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
   ReceiptConfiguration(OracleGateway()).sku_rule(f["ware"],f["article"],{"pick_cell":f["case_cell"],"temp_min":None,"temp_max":None,"min_shelf_days":0},"admin")
  mass=QualityWeightPolicy(OracleGateway());old=mass.get(f["ware"],f["article"])
  if old["base_weight_kg"]!="4"or old["box_weight_kg"]!="10":
   mass.set(f["ware"],f["article"],WeightPolicyInput(expected_version=int(old["version"]),base_uom="EA",base_weight_kg="4",box_weight_kg="10"),"admin")
  admission=OutgoingQuality(OracleGateway())
  if not posted("MIXED172.SHIP"):
   signature=admission.status(f["shipment"])["composition_signature"]
   quality={"quality_kind":"SCAN","error_count":0,"note":"Owned172 synthetic independent control input","expected_composition_signature":signature}
   q.execute("select BARCODE_SHT from RRL_ARTICULS where ACTICUL=:p_article",p_article=f["article"]);barcode=q.fetchone()[0]
   scans=[{"scan_id":"MIXED172.ITEM:"+str(i),"barcode":barcode,"quantity":"1"}for i in range(1,4)]
   post("OUTGOING_PALLET_CHECK",{"pallet_identifier":f["shipment"]},{**quality,"item_scans":scans},"MIXED172.QC.SCAN.COVERED",f["controller"])
   post("OUTGOING_PALLET_CHECK",{"pallet_identifier":f["shipment"]},{**quality,"quality_kind":"WEIGHT","gross_weight":"12","wood_weight":"0"},"MIXED172.QC.WEIGHT",f["controller"])
   assert admission.status(f["shipment"])["ready"]
  post("SHIP_PALLET",{"pallet_identifier":f["shipment"]},{},"MIXED172.SHIP","admin")
  api(f"/case-pick/tasks/{f['case']}/return-carrier",{"operation_id":"MIXED172.EMPTY","scan_container":f["carrier"],"expected_content_version":0,"destinations":{},"allow_empty":True,"reason":"Unused second owned order stays in planning"})
  decision={"operation_id":"MIXED172.FINISH","disposition":"PARTIAL_SHIPPED_RETURNED","reason":"Full order physically shipped3; empty second order remains1"}
  if not posted(decision["operation_id"]):
   preview=client.get(base+f"/picking/waves/{f['wave']}/execution");assert preview.status_code==200
   assert preview.json()["mixed_decision"]["eligible"]and not preview.json()["ready"]
   wrong=client.post(base+f"/picking/waves/{f['wave']}/finish-execution",json={**decision,"operation_id":"MIXED172.WRONG_ALL_RETURNED","disposition":"RETURNED_TO_PLANNING"});assert wrong.status_code==409
   rollback=StockCommand(operation_id="MIXED172.FINISH.UNCOMMITTED",command_type="WAVE_EXECUTION_FINISH",actor="admin",lines=(),source={"wave_id":f["wave"]},metadata={"disposition":decision["disposition"],"reason":decision["reason"]})
   inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,rollback.canonical_json());out=q.var(oracledb.DB_TYPE_CLOB)
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   try:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out]);q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=f["wave"]);assert q.fetchone()[0]=="DONE"
   finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
   q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=f["wave"]);assert q.fetchone()[0]=="LAUNCHED"
  def finish():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as parallel:
    r=parallel.post(base+f"/picking/waves/{f['wave']}/finish-execution",json=decision)
    assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:finish(),range(2)))
  assert results[0]==results[1]and results[0]["completion_outcome"]=="MIXED_SHIPPED_AND_RETURNED"
  assert not results[0]["order_fulfillment_changed"]and not results[0]["physical_stock_changed"]
  q.execute("select STATUS,FACT_QTY,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:p_ff",p_ff=f["ff"]);assert q.fetchone()==("SHIPPED",3,"MIXED172.SHIP")
  for key,quantity in[("full","0"),("empty","1")]:
   q.execute("select RRL_STOCK_POOL_READ.line_snapshot_json(:p_row)from dual",p_row=f[key]["row"]);raw=q.fetchone()[0];line=json.loads(raw.read()if hasattr(raw,"read")else raw);assert line["quantity"]==quantity,(key,line)
  print("PASS172 actual full3 native move/independent synthetic BOTH QC/shipment + empty1 cancellation -> mixed wave403 decision; wrong all-returned409/late rollback/concurrent one receipt; current original line quantities0 and1 preserved")
 finally:
  q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=f["wave"]);done=q.fetchone()[0]=="DONE"
  if done:
   q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r where r.UID_POLETA in(:p_full,:p_case)and r.REMAIN>0",p_full=f["full_uid"],p_case=f["case_uid"])
   counts=[{"uid":uid,"cell":cell,"article":f["article"],"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]}for uid,cell,unit,version in q.fetchall()]
   if counts:post("INVENTORY_COUNT",{"revision_id":f["revision"]},{"reason":"Retire own172 remaining source fixture quantity","counts":counts},"MIXED172.CLEAN")
  else:print("Owned172 wave pending; native goods/reservations preserved for same-operation recovery")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("Original135 P20H20 unchanged; own remaining source fixture cleared only after completed wave; no real hardware/SAP/Gov acceptance claimed")
