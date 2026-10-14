"""Actual full-pallet move -> existing ST binding -> pinned shipment; clean only own P/H through root."""
import json,sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
import httpx,xml.etree.ElementTree as ET
from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
from app.modules.inventory.infrastructure.quality_scope import QualityScope
folder=Path("reports/retailcase/2026-10-13/codex/QC_F1");manifest=folder/"native_fixture.json"
assert manifest.exists(),"Fixture required"
cfg=get_settings();tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="QCF1.ST:"+tag;receive="QR"+tag;article="QCF1.SKU."+tag;address="QCF1.ADDR."+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**b):
  if ":ware" in sql:b["ware"]=ware
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","finished_goods_edit" if "RRL_SKU_RECEIPT_POLICY" in sql else "warehouse_settings_edit"])
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
 result=json.loads(manifest.read_text(encoding='utf-8'));tag=result['tag'];ware=result['warehouse'];article=result['article'];lot=result['lot'];src=result['source_cell'];dst=result['target_cell'];receive=result['receive_cell'];st_uid=result['shipment'];address='QCF1.ADDR.'+tag
 order=result['order_id'];wave=result['wave_id'];task=result['task_id'];st=result['st_id'];ff=result['fulfillment_id'];revision=result['revision_id']
 def save():manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 q.execute('select PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ID from RRL_PICK_TASK where CUSTOMER_ORDER_ID=:order_id',order_id=order);pt,plan,pl,customer=q.fetchone()
 imported={'order_id':result['supply_order_id']}
 q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
 client=httpx.Client(auth=('admin',password),base_url='http://127.0.0.1:8088',timeout=40)
 def api(path,body=None,xml=None,status=200):
  response=client.post(path,json=body)if xml is None else client.post(path,content=xml,headers={'Content-Type':'application/xml'})
  assert response.status_code==status,response.text
  return response.json()
 def fields(node,values):
  for key,value in values.items():ET.SubElement(node,key).text=str(value)
 meta('update RRL_CELLS set OTBOR=0,LIMIT_WEIGHT=0,LIMIT_HEIGHT=0 where CELL=:cell',cell=src)
 pick_reference='QP'+tag
 meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)select :cell,:ware,1,1,0,1,0,0,0 from dual where not exists(select 1 from RRL_CELLS where CELL=:cell)",cell=pick_reference)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD having not exists(select 1 from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL',:cell))",cell=pick_reference)
 meta('update RRL_RECEIPT_SKU_RULE set PICK_CELL=:cell where WARE_ID=:ware and ARTICUL=:a',cell=pick_reference,a=article)
 try:
  receipt=api('/api/receiving/supply-orders/'+imported['order_id']+'/pallets',{'operation_id':'QCF1.RECEIPT:'+tag,'line_number':'1','pallet_identifier':lot,'quantity':'3','supplier_batch':'QCF1.BATCH:'+tag,'expiry_date':'2030-01-01','gross_weight':'3','product_barcode':'QCF1.BAR.'+tag,'units':[],'aggregations':[]},status=201)
  result['receipt']=receipt;result['stage']='RECEIVED';save()
  putaway=api('/api/receiving/putaway/'+str(receipt['task_id'])+'/complete',{'scanned_pallet':lot,'scanned_from_cell':receive,'scanned_to_cell':receipt['putaway_cell']})
  assert receipt['putaway_cell']==src;result['putaway']=putaway;save()
  post('RESERVATION_CREATE',{'uid_pallet':lot,'cell':src,'articul':article,'qty':'3','unit_code':'EA','ware_id':ware,'reservation_kind':'HARD','reservation_scope':'PALLET','reservation_domain':'PICKING','source_doc_type':'PICK_WAVE','source_doc_id':wave,'source_line_id':pt,'customer_order_id':order,'customer_id':customer,'pick_plan_id':plan,'pick_plan_line_id':pl},{'type':'PICK_WAVE','id':wave})
  post('WAVE_PICK_RELEASE',{},{'wave_id':wave})
  completed=post('TASK_COMPLETE',{'fact_qty':'3','scanned_pallet':lot,'scanned_from_cell':src,'scanned_to_cell':dst},{'task_id':task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  bound=post('PICK_PALLET_BIND_SHIPMENT',{'shipment_identifier':st_uid,'scanned_pallet':lot,'expected_stock_version':int(preview['stock_version'])},{'task_id':task},'QCF1.BIND:'+tag)
  result.update(completed=completed,binding=bound,stage='BOUND');save()
  scope=QualityScope(OracleGateway());policy={'operation_id':'QCF1.POLICY:'+tag,'expected_version':0,'store_addr':address,'place_category':'STOCK','active':True,'control_mode':'WEIGHT','independent':False,'sample_percent':'0','exempt_whole':False,'exempt_storage':True,'reason':'Own real native full pallet storage identifier proof'}
  saved=scope.save(ware,'admin',policy);result['policy']=saved;save()
  admission=OutgoingQuality(OracleGateway());status=admission.status(st_uid);result['before_plan']=status;save()
  assert status['weight_exemption']['eligible']and status['weight_exemption']['exemption_basis']=='SCANNED_ORIGINAL_STORAGE_IDENTIFIER',status
  qcop='QCF1.PLAN:'+tag
  qc=post('OUTGOING_PALLET_CHECK',{'quality_kind':'PLAN'},{'pallet_identifier':st_uid},qcop)
  assert qc['control_status']['ready'],qc
  repeated=post('OUTGOING_PALLET_CHECK',{'quality_kind':'PLAN'},{'pallet_identifier':st_uid},qcop);assert qc==repeated
  q.execute('select count(*)from RRL_QC_EXEMPT_FACT where OPERATION_ID=:op and DOCUMENT_ID=:doc',op=qcop,doc=st);assert q.fetchone()[0]==1
  q.execute('select PAYLOAD_JSON from RRL_QC_EXEMPT_FACT where OPERATION_ID=:op and DOCUMENT_ID=:doc',op=qcop,doc=st);audit=read_oracle_json(q.fetchone()[0]);assert audit['storage_pick_task_id']==task and audit['base_quantity']=='3'
  q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell',p_uid=lot,cell=dst);assert q.fetchone()==(3,3)
  result.update(qc=qc,audit=audit,replay_exact=True,stage='PASS');save();print('PASS SAP receipt -> putaway -> native fullpal move/bind -> storage-only QC PLAN/audit1/exact replay; P3H3')
 finally:
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",w=wave)
  for(rid,)in q.fetchall():post('RESERVATION_RELEASE',{'reason':'End private QC F1 fixture'},{'reservation_id':int(rid)})
  q.execute('select UID_POLETA,CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and REMAIN>0',p_uid=lot)
  counts=[{'uid':u,'cell':cell,'article':article,'unit':unit,'quantity':'0','expected_stock_version':int(version),'unit_keys':[]}for u,cell,unit,version in q.fetchall()]
  if counts:post('INVENTORY_COUNT',{'reason':'End private QC F1 fixture','counts':counts},{'revision_id':revision})
  meta('update RRL_QC_SCOPE_RULE set ACTIVE_FLAG=0,RULE_VERSION=RULE_VERSION+1 where WARE_ID=:ware and STORE_ADDR=:addr',addr=address)
  result['cleanup']='own P/H cleared through root; own policy inactive; audit retained';save();client.close()
