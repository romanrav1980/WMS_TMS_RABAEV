"""Own Oracle fixture: graph -> native marked birth; no government ACK."""
import json,sys
from pathlib import Path
from uuid import uuid4
from copy import deepcopy
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.trace_sender_manifest import TraceSenderManifest
from app.modules.inventory.infrastructure.inventory_observations import InventoryObservations
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_trace_manifest import TraceManifestError
from app.modules.inventory.contracts_observations import InventoryObservationError
cfg=get_settings();tag=uuid4().hex[:10];article='QMAN'+tag;cell='QM'+tag
ware=100000+int(tag[:6],16);prefix='0460000000000'
gtin=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
pallet_prefix='100'+str(int(tag,16)).zfill(14)
pallet=pallet_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(pallet_prefix)))%10)%10)
op='MANIFEST.IMPORT:'+tag;birth='MANIFEST.BIRTH:'+tag
gateway=OracleGateway();service=TraceSenderManifest(gateway);stock=InventoryObservations(gateway,StockPosting())
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**binds):
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:q.execute(sql,binds);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");old=q.fetchone()[0]
 q.execute('select count(*)from RRL_WARES where ID=:w',w=ware);assert q.fetchone()[0]==0
 meta('declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;r.BARCODE_SHT:=:gtin;insert into RRL_ARTICULS values r;end;',old=old,a=article,gtin=gtin)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Sender fixture' from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=old)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,1,'admin')",a=article)
 for system,profile,scan_mode in [('CRPT','TOBACCO','PALLET'),('EGAIS','ALCOHOL','BOX')]:
  meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)values(:a,:s,:p,'QA1',:scan_mode)",a=article,s=system,p=profile,scan_mode=scan_mode)
 for kind,key in [('SKU',article)]:
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key(:kind,:k),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",kind=kind,k=key)
 meta("insert into RRL_WARES(ID,NAME,PREFIX,BLOCK_IF_NO_PROOVE)values(:w,:n,'QM',1)",w=ware,n='Sender '+tag)
 meta('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM)values(:c,:w,0,0,0,0,0)',c=cell,w=ware)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 revision=int(q.callfunc('REVIZION.create_revizion',oracledb.DB_TYPE_NUMBER,[ware,'admin']));conn.commit()
 units=[{'unit_id':str(i),'quantity':'1','codes':[{'system_code':'CRPT','profile_code':'TOBACCO','code':gtin+tag[:5]+str(i).zfill(2)},{'system_code':'EGAIS','profile_code':'ALCOHOL','code':('QA'+tag+str(i)).ljust(68,'X')}]}for i in range(3)]
 def agg(identity,system,profile,level,ids,children):
  return {'aggregation_id':identity,'system_code':system,'profile_code':profile,'level':level,'code':identity+':'+tag,'unit_ids':ids,'children':children}
 aggregates=[agg('CRPT.BOX1','CRPT','TOBACCO','BOX',['0','1'],[]),agg('CRPT.BOX2','CRPT','TOBACCO','BOX',['2'],[]),agg('CRPT.PALLET','CRPT','TOBACCO','PALLET',[],['CRPT.BOX1','CRPT.BOX2']),agg('EGAIS.BOX','EGAIS','ALCOHOL','BOX',['0','1','2'],[])]
 doc={'contract_version':'WmsTraceManifest.v1','source_kind':'INVENTORY','source_document_id':revision,'warehouse_id':ware,'pallet_identifier':pallet,'article':article,'base_uom':'EA','policy_version':1,'profile_versions':[{'system_code':s,'profile_code':p,'version':'QA1'}for s,p in [('CRPT','TOBACCO'),('EGAIS','ALCOHOL')]],'units':units,'aggregations':aggregates,'document_reference':'Synthetic sender '+tag}
 raw=json.dumps(doc,separators=(',',':'));result=service.import_manifest(op,raw,'admin')
 assert result['physical_unit_count']==3 and result['aggregate_count']==4 and result['quantity']=='3' and not result['stock_changed']
 assert service.import_manifest(op,raw,'admin')==result
 try:service.import_manifest(op,raw+' ','admin');raise AssertionError('Changed raw accepted')
 except TraceManifestError as exc:assert exc.code=='TRACE_MANIFEST_PAYLOAD_CONFLICT'
 broken=deepcopy(doc);broken['aggregations'][0]['children']=['CRPT.PALLET']
 try:service.import_manifest(op+'.CYCLE',json.dumps(broken),'admin');raise AssertionError('Cycle accepted')
 except TraceManifestError as exc:assert exc.status==422
 q.execute('select count(*)from RRL_PALLETS where UID_PALLET=:p',p=pallet);assert q.fetchone()[0]==0
 scans=[{k:a[k]for k in ['system_code','profile_code','level','code']}for a in aggregates if a['aggregation_id']in ['CRPT.PALLET','EGAIS.BOX']]
 capture={'manifest_operation_id':op,'units':[],'aggregations':scans}
 body={'uid':pallet,'cell':cell,'article':article,'quantity':'3','expiry_date':'2030-01-01','price':'0','reason':'Synthetic native birth','birth_captures':{pallet:capture}}
 meta("update RRL_SKU_RECEIPT_PROFILE set PROFILE_VERSION='QA2' where ARTICUL=:a and SYSTEM_CODE='CRPT'",a=article)
 try:stock.register_lot(birth,revision,body,'admin');raise AssertionError('Obsolete manifest accepted')
 except InventoryObservationError as exc:assert exc.status==409,str(exc)
 doc['profile_versions'][0]['version']='QA2';new_op=op+'.CURRENT'
 result=service.import_manifest(new_op,json.dumps(doc),'admin');capture['manifest_operation_id']=new_op
 posted=stock.register_lot(birth,revision,body,'admin')
 assert stock.register_lot(birth,revision,body,'admin')==posted
 q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:c',p=pallet,c=cell);assert q.fetchone()==(3,0)
 q.execute('select count(*)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p',p=pallet);assert q.fetchone()[0]==3
 q.execute('select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p',p=pallet);assert q.fetchone()[0]==6
 q.execute('select STOCK_OPERATION_ID from RRL_TRACE_MANIFEST_USE where MANIFEST_OPERATION_ID=:op',op=new_op);assert q.fetchone()[0]==birth
 q.execute('select count(*)from RRL_WMS_RECEIPT_AGG where UID_PALLET=:p',p=pallet);assert q.fetchone()[0]==2
 evidence={'tag':tag,'warehouse_id':ware,'revision_id':revision,'pallet_identifier':pallet,'article':article,'cell':cell,'manifest_operation_id':new_op,'stock_operation_id':birth,'physical_quantity':'3','physical_units':3,'code_identities':6,'scanned_aggregates':2,'government_ack':False}
 print('PASS nested sender4 / scans2 / physical3 / codes6 / P3H0 / replay / conflict / cycle / obsolete denial',flush=True)
 print(json.dumps(evidence),flush=True)
