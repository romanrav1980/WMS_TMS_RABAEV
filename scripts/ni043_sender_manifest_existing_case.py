"""Continue same operation after confirmed deferred FK rollback; do not create new fixture."""
import json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.inventory_observations import InventoryObservations
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.platform.public import read_oracle_json
cfg=get_settings();op='MANIFEST.IMPORT:a3b49b8174.CURRENT';birth='MANIFEST.BIRTH:a3b49b8174'
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn)as conn:
 q=conn.cursor();q.execute('select RAW_JSON from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID=:op',op=op);doc=read_oracle_json(q.fetchone()[0])
 pallet=doc['pallet_identifier'];article=doc['article'];revision=doc['source_document_id'];ware=doc['warehouse_id']
 q.execute('select CELL from RRL_CELLS where WARE_ID=:ware',ware=ware);cell=q.fetchone()[0]
 scans=[{k:a[k]for k in ['system_code','profile_code','level','code']}for a in doc['aggregations']if a['aggregation_id']in ['CRPT.PALLET','EGAIS.BOX']]
 capture={'manifest_operation_id':op,'units':[],'aggregations':scans}
 body={'uid':pallet,'cell':cell,'article':article,'quantity':'3','expiry_date':'2030-01-01','price':'0','reason':'Synthetic native birth','birth_captures':{pallet:capture}}
 stock=InventoryObservations(OracleGateway(),StockPosting());result=stock.register_lot(birth,revision,body,'admin')
 assert stock.register_lot(birth,revision,body,'admin')==result
 q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:c',p=pallet,c=cell);assert q.fetchone()==(3,0)
 for table,count in [('RRL_WMS_RECEIPT_UNIT',3),('RRL_WMS_RECEIPT_CODE',6),('RRL_WMS_RECEIPT_AGG',2)]:
  q.execute('select count(*)from '+table+' where UID_PALLET=:p',p=pallet);assert q.fetchone()[0]==count
 q.execute('select STOCK_OPERATION_ID from RRL_TRACE_MANIFEST_USE where MANIFEST_OPERATION_ID=:op',op=op);assert q.fetchone()[0]==birth
 evidence={'warehouse_id':ware,'revision_id':revision,'pallet_identifier':pallet,'article':article,'cell':cell,'manifest_operation_id':op,'stock_operation_id':birth,'physical_quantity':'3','physical_units':3,'code_identities':6,'scanned_aggregates':2,'government_ack':False}
 print('PASS original graph4/scans2/physical3/codes6/P3H0/replay; no fabricated SAP receipt or government ACK',flush=True)
 print(json.dumps(evidence),flush=True)
