"""Current nonadmin warehouse scope: own native MES completion movement -> sender aggregate capture -> one root stock birth."""
import json,sys
from pathlib import Path
from uuid import uuid4
from copy import deepcopy
from datetime import date
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.services.bom_service import BomService
from app.services.mes_service import MesService
from app.schemas import BomCreateRequest,BomLineRequest,MesProductionOrderCreateRequest,MesCompleteOrderRequest,MesCompletionPallet
cfg=get_settings();tag=uuid4().hex[:10];uid='MES.MARKED.INTERNAL.PALLET:'+tag
admin=httpx.Client(auth=('admin','admin123'),timeout=35);active=admin;actor='QM127'+tag;group=actor.upper();secret=uuid4().hex;receiver=httpx.Client(auth=(actor,secret),timeout=35);base='http://127.0.0.1:8088'
def api(method,path,body=None,status=200):
 r=active.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute("select RAW_JSON from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID='MANIFEST.IMPORT:a3b49b8174.CURRENT'");doc=deepcopy(read_oracle_json(q.fetchone()[0]))
 article=doc['article'].upper();doc['article']=article;ware=doc['warehouse_id'];q.execute('select CELL from RRL_CELLS where WARE_ID=:w',w=ware);cell=q.fetchone()[0]
 bom_service=BomService(OracleGateway())
 bom=bom_service.create_bom(BomCreateRequest(bom_code='QM126:'+tag,target_articul=article,target_gtin=doc['units'][0]['codes'][0]['code'][:14],base_qty=3,base_unit_code='EA',valid_from=date(2026,10,1),ware_id=ware,created_by='admin'))
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");raw_article=q.fetchone()[0]
 bom_service.add_line(bom,BomLineRequest(component_type='RAW',component_articul=raw_article,qty_per_base=3,unit_code='EA',created_by='admin'))
 bom_service.approve_bom(bom,'admin')
 order=MesService(OracleGateway()).create_order(MesProductionOrderCreateRequest(order_no='QM126:'+tag,bom_id=bom,target_articul=article,planned_qty=3,unit_code='EA',ware_id=ware,created_by='admin',idempotency_key='QM126.ORDER:'+tag))
 completion=MesService(OracleGateway()).complete_order(order,MesCompleteOrderRequest(prod_batch_no='QM126.LOT:'+tag,fact_qty=3,unit_code='EA',pallets=[MesCompletionPallet(uid_pallet=uid,pallet_no=1,quantity=3,target_ware_id=ware,target_cell=cell)],idempotency_key='QM126.COMPLETE:'+tag,created_by='admin'))
 q.execute("select MOVEMENT_ID,STATUS from RRL_MES_MOVEMENT where PRODUCTION_ORDER_ID=:o and MOVEMENT_TYPE='FG_PALLET_RELEASE' and UID_PALLET=:lot_id",o=order,lot_id=uid);movement,state=q.fetchone();assert state=='MES_POSTED'
 q.execute('select count(*)from RRL_REMAINS where UID_POLETA=:lot_id',lot_id=uid);assert q.fetchone()[0]==0
 doc.update(source_kind='MES',source_document_id=int(movement),pallet_identifier=uid,document_reference='Own MES126 '+tag)
 for unit in doc['units']:
  for code in unit['codes']:
   code['code']=code['code'][:14]+tag[:5]+unit['unit_id'].zfill(2) if code['system_code']=='CRPT' else ('QA'+tag+unit['unit_id']).ljust(68,'X')
 for agg in doc['aggregations']:agg['code']=agg['aggregation_id']+':'+tag
 manifest={'operation_id':'MES126.MANIFEST:'+tag,'manifest_json':json.dumps(doc,separators=(',',':'))}
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own MES scope receiver',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api('POST','/api/admin/rights/groups',{'id':group,'name':'Own MES scope receiver'})
 for right in ['trace_manifest_import','mes_wms_bridge_apply']:
  api('POST',f'/api/admin/rights/groups/{group}/rights',{'right_name':right,'description':'Own MES scope'})
 active=receiver
 api('POST','/api/inventory/trace-manifests',manifest)
 scans=[{k:a[k]for k in ['system_code','profile_code','level','code']}for a in doc['aggregations']if a['aggregation_id']in ['CRPT.PALLET','EGAIS.BOX']]
 body={'operation_id':'MES126.BIRTH:'+tag,'movement_ids':[int(movement)],'units_by_movement':{},'birth_captures':{uid:{'manifest_operation_id':manifest['operation_id'],'units':[],'aggregations':scans}}}
 path=f'/api/mes/production-orders/{order}/apply-wms'
 wrong=deepcopy(body);wrong['operation_id']+='.FOREIGN';wrong['birth_captures'][uid]['manifest_operation_id']='MANIFEST.IMPORT:a3b49b8174.CURRENT'
 api('POST',path,wrong,409)
 q.execute('update RUSERS set WARE_ID=9104 where ID=:id',id=actor);c.commit()
 denied=api('POST',path,body,403);assert denied['detail']['code']=='MES_CURRENT_WAREHOUSE_ACTOR_REQUIRED'
 q.execute('select count(*)from RRL_REMAINS where UID_POLETA=:lot_id',lot_id=uid);assert q.fetchone()==(0,)
 q.execute('update RUSERS set WARE_ID=:ware where ID=:id',ware=ware,id=actor);c.commit()
 result=api('POST',path,body);assert api('POST',path,body)==result
 q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=uid,cell=cell);assert q.fetchone()==(3,0)
 q.execute('select STATUS,STOCK_OPERATION_ID,POSTED_BASE_QTY from RRL_MES_MOVEMENT where MOVEMENT_ID=:id',id=movement);assert q.fetchone()==('APPLIED_TO_WMS',body['operation_id'],3)
 q.execute('select count(*)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:lot_id',lot_id=uid);assert q.fetchone()[0]==3
 q.execute('select STOCK_OPERATION_ID from RRL_TRACE_MANIFEST_USE where MANIFEST_OPERATION_ID=:op',op=manifest['operation_id']);assert q.fetchone()[0]==body['operation_id']
 q.execute('update RUSERS set DELETED=1 where ID=:id',id=actor);c.commit()
 print('PASS127 current native/API warehouse scope/nonadmin right/foreign403/no partial P/current source -> existing MES original native MES FG movement '+str(movement)+' / order '+str(order)+' / completion '+str(completion)+' / internalUID / exact sender graph / P3H0 / physical3 / native JSON replay / foreign source409; operation='+body['operation_id'],flush=True)
 print('Synthetic standalone FG release only; no claim of real raw consumption, factory readiness, or government ACK.',flush=True)
