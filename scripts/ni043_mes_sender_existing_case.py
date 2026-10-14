"""Continue the original native completion; no second production fixture."""
import json,sys
from pathlib import Path
from copy import deepcopy
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.services.mes_service import MesService
from app.schemas import MesCompleteOrderRequest,MesCompletionPallet
s=get_settings();tag='9643f7c26e';uid='MES.MARKED.INTERNAL.PALLET:'+tag;order=98;movement=120
admin=httpx.Client(auth=('admin','admin123'),timeout=35);base='http://127.0.0.1:8088'
def api(method,path,body=None,status=200):
 r=admin.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute("select RAW_JSON from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID='MANIFEST.IMPORT:a3b49b8174.CURRENT'");doc=deepcopy(read_oracle_json(q.fetchone()[0]))
 old=doc['article'];article=old.upper();ware=doc['warehouse_id'];q.execute('select CELL from RRL_CELLS where WARE_ID=:w',w=ware);cell=q.fetchone()[0]
 def meta(sql,**binds):
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 q.execute('select count(*)from RRL_ARTICULS where ACTICUL=:a',a=article)
 if q.fetchone()[0]==0:
  meta('declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;insert into RRL_ARTICULS values r;end;',old=old,a=article)
  meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'MES own upper fixture'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=old)
  meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,1,'admin')",a=article)
  meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)select :a,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:old",a=article,old=old)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 # The native completion API stores a default target; existing service configures requested target/task.
 MesService(OracleGateway()).complete_order(order,MesCompleteOrderRequest(prod_batch_no='QM126.LOT:'+tag,fact_qty=3,unit_code='EA',pallets=[MesCompletionPallet(uid_pallet=uid,pallet_no=1,quantity=3,target_ware_id=ware,target_cell=cell)],idempotency_key='QM126.COMPLETE:'+tag,created_by='admin'))
 doc.update(source_kind='MES',source_document_id=movement,pallet_identifier=uid,document_reference='Own MES126 '+tag,article=article)
 for unit in doc['units']:
  for code in unit['codes']:
   code['code']=code['code'][:14]+tag[:5]+unit['unit_id'].zfill(2) if code['system_code']=='CRPT' else ('QA'+tag+unit['unit_id']).ljust(68,'X')
 for agg in doc['aggregations']:agg['code']=agg['aggregation_id']+':'+tag
 manifest={'operation_id':'MES126.MANIFEST:'+tag,'manifest_json':json.dumps(doc,separators=(',',':'))}
 api('POST','/api/inventory/trace-manifests',manifest)
 scans=[{k:a[k]for k in ['system_code','profile_code','level','code']}for a in doc['aggregations']if a['aggregation_id']in ['CRPT.PALLET','EGAIS.BOX']]
 body={'operation_id':'MES126.BIRTH:'+tag,'movement_ids':[movement],'units_by_movement':{},'birth_captures':{uid:{'manifest_operation_id':manifest['operation_id'],'units':[],'aggregations':scans}}}
 path=f'/api/mes/production-orders/{order}/apply-wms';wrong=deepcopy(body);wrong['operation_id']+='.FOREIGN';wrong['birth_captures'][uid]['manifest_operation_id']='MANIFEST.IMPORT:a3b49b8174.CURRENT'
 api('POST',path,wrong,409)
 result=api('POST',path,body);assert api('POST',path,body)==result
 q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=uid,cell=cell);assert q.fetchone()==(3,0)
 q.execute('select STATUS,STOCK_OPERATION_ID,POSTED_BASE_QTY from RRL_MES_MOVEMENT where MOVEMENT_ID=:id',id=movement);assert q.fetchone()==('APPLIED_TO_WMS',body['operation_id'],3)
 q.execute('select count(*)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:lot_id',lot_id=uid);assert q.fetchone()[0]==3
 q.execute('select STOCK_OPERATION_ID from RRL_TRACE_MANIFEST_USE where MANIFEST_OPERATION_ID=:op',op=manifest['operation_id']);assert q.fetchone()[0]==body['operation_id']
 print('PASS126 original completion/order98/movement120 / native service target / marked sender graph / internalUID / P3H0 / physical3 / HTTP nativeJSON replay / foreign source409',flush=True)
 print('Synthetic FG release only; no real raw consumption, factory readiness, or government ACK.',flush=True)
