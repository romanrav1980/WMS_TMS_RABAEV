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
assert not manifest.exists(),"Resume existing fixture explicitly"
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
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
 client=httpx.Client(auth=('admin',password),base_url='http://127.0.0.1:8088',timeout=40)
 def api(path,body=None,xml=None,status=200):
  response=client.post(path,json=body)if xml is None else client.post(path,content=xml,headers={'Content-Type':'application/xml'})
  assert response.status_code==status,response.text
  return response.json()
 def fields(node,values):
  for key,value in values.items():ET.SubElement(node,key).text=str(value)
 root=ET.Element('ARTMAS10');document=ET.SubElement(root,'IDOC');fields(ET.SubElement(document,'EDI_DC40'),{'DOCNUM':'146'+str(int(tag,16)),'IDOCTYP':'ARTMAS10','MESTYP':'ARTMAS','SNDPOR':'OWN.QA.SAP','SNDPRN':'OWN.QA.SAP','CREDAT':'20761014','CRETIM':'100000'})
 fields(ET.SubElement(document,'E1BPE1MATHEAD'),{'MATERIAL':article})
 fields(ET.SubElement(document,'E1BPE1MARART'),{'MATERIAL':article,'BASE_UOM':'EA','EAN_UPC':'QCF1.BAR.'+tag})
 fields(ET.SubElement(document,'E1BPE1MAKTRT'),{'MATERIAL':article,'LANGU_ISO':'EN','MATL_DESC':'Own QC storage binding '+tag})
 fields(ET.SubElement(document,'E1BPE1MARMRT'),{'MATERIAL':article,'ALT_UNIT':'EA','NUMERATOR':'1','DENOMINATR':'1','EAN_UPC':'QCF1.BAR.'+tag})
 api('/api/integrations/sap/artmas',xml=ET.tostring(root,encoding='utf-8'),status=202)
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 ware=100000+int(tag[:6],16)
 result={'tag':tag,'warehouse':ware,'article':article,'lot':lot,'source_cell':src,'target_cell':dst,'receive_cell':receive,'shipment':st_uid,'stage':'SETUP'}
 def save():manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 save()
 meta("insert into RRL_WARES(ID,NAME,PREFIX,BLOCK_IF_NO_PROOVE) values(:ware,:n,:p,1)",n="QC private "+tag,p="Q"+tag[:2])
 meta("update RRL_ARTICULS set TYPE_W=0 where ACTICUL=:a",a=article)
 for cell in (src,dst,receive,"QP"+tag):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,:pick,:pick,0,:pick,0,0,0)",c=cell,pick=int(cell=="QP"+tag))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 meta("update RRL_WARES set DEFAULT_RECEIVE_CELL=:cell where ID=:ware",cell=receive)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:article,1,0,'admin')",article=article)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:ware,:article,:cell,0,0,'DIRECT')",article=article,cell="QP"+tag)
 meta("insert into RRL_ADDR(ADDR,DELETED3)values(:address,0)",address=address)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 order,row,plan,pl,pt,wave,wt,task,st,ff=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")]
 result.update(order_id=order,wave_id=wave,task_id=task,st_id=st,fulfillment_id=ff,revision_id=revision);save()
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:ware)",id=order,no=lot,c=customer)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(:id,:o,1,:a,3,'EA')",id=row,o=order,a=article)
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS) values(:id,:o,:c,:ware,'RELEASED')",id=plan,o=order,c=customer)
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS) values(:id,:p,:r,:a,3,3,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
 meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY) values(:id,:p,:pl,:o,:c,'FULL_PALLET','NEW',:a,:u,:src,:dst,3)",id=pt,p=plan,pl=pl,o=order,c=customer,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:ware,'LAUNCHED','admin')",id=wave,code=lot)
 meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE) values(:id,:w,:p,'FULL_PALLET','NEW',:a,:u,3,:src,:dst)",id=wt,w=wave,p=pt,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY) values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:w,:u,:src,:dst,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=wt,w=wave,u=lot,src=src,dst=dst)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:u,:u,:ware,0,:addr)",id=st,u=st_uid,addr=address)
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'EA',3)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 try:
  supply=ET.Element('WarehouseSupplyOrder',version='1');fields(supply,{'Sender':'OWN.QA.SAP','MessageId':'QCF1.SUPPLY:'+tag,'OrderNumber':'QCF1:'+tag,'Revision':1,'WarehouseId':ware,'ReceiveCell':receive,'Supplier':'Own QC F1 fixture'})
  line=ET.SubElement(ET.SubElement(supply,'Lines'),'Line');fields(line,{'LineNumber':'1','Material':article});ET.SubElement(line,'Quantity',unit='EA').text='3'
  imported=api('/api/integrations/sap/supply-orders',xml=ET.tostring(supply,encoding='utf-8'),status=202);result['supply_order_id']=imported['order_id'];save()
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
