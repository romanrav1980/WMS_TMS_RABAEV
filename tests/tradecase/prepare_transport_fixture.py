"""Prepare an owned synthetic legacy ST through existing writers; no physical stock seed."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import json,sys,os
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.store_source_scope import source_transaction
from app.modules.fulfillment.infrastructure.legacy_preparation import LegacyPreparation
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb
P=Path(os.environ.get('TRADECASE_TRANSPORT_FIXTURE',str(ROOT/'runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1155.json')))
s=json.loads(P.read_text())if P.exists()else dict(warehouse_id=215590763,case_id=1155,order_id=2185,article='TC03554EEBF3',st_number='TC7.1155',st_pallet='TC7.PALLET.1155',address='TRADECASE.QA.1155',origin='SYNTHETIC_NATIVE_ST_METADATA_NOT_SAP')
def save():P.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
if 'legacy_order_id'not in s:
 with oracle_connection()as c:
  q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute('select COUNT_SHT_IN_KOR,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X,DIMKOR_Y,DIMKOR_Z from RRL_ARTICULS where ACTICUL=:a',a=s['article']);s['original_logistics']=list(q.fetchone());s['setup_note']='Prior attempt committed synthetic logistics before ST transaction rolled back; no physical quantity changed';save()
   q.execute('update RRL_ARTICULS set COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=1.2,DIMKOR_X=0.4,DIMKOR_Y=0.3,DIMKOR_Z=0.2,CELL=:pick_cell where ACTICUL=:a',a=s['article'],pick_cell='T3P554eebf3');assert q.rowcount==1;c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 prep=LegacyPreparation(OracleGateway())
 with source_transaction(OracleGateway(),'Owned TRADECASE synthetic ST metadata','admin','customer_order_import',warehouse=s['warehouse_id'])as q:
  q.execute('select count(*)from RRL_ORDERS where ORD_NUMBER=:n',n=s['st_number']);assert q.fetchone()[0]==0
  date=datetime(2026,11,1)
  legacy=q.callfunc('ORDERS.CREATE_ORDER',oracledb.DB_TYPE_NUMBER,[s['st_number'],date,s['warehouse_id'],s['address'],'1',date,'admin']);assert legacy>0
  rows=prep._legacy_rows(q,legacy,s['warehouse_id'],{s['article']:(Decimal(s.get('quantity',100)),'EA')})
  pallet=q.callfunc('RRL_SBORKA_PALLETS_ADD2',oracledb.DB_TYPE_NUMBER,[s['st_number'],s['address'],1,s['st_pallet'],'1',date,'','admin',s['warehouse_id']]);assert pallet>0
  q.execute('update RRL_SBORKA_PALLETS set ORIGINAL_ORDER_NUMBER=:n,ORIGINAL_ST_NUMBER=:n,CONDITION=0 where ID=:id',n=s['st_number'],id=pallet)
  prep._pallet_rows(q,s['st_pallet'],[dict(articul=s['article'],quantity=str(s.get('quantity',100)))],rows,s['warehouse_id'],s['st_number'])
  q.execute("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,:o,:pid,:p,:addr,'PLANNED',0,0,'TRADECASE_QA',sysdate,'admin')",o=s['order_id'],pid=pallet,p=s['st_pallet'],addr=s['address'])
  q.execute('update RRL_CUSTOMER_ORDER set LEGACY_ORDER_ID=:l where CUSTOMER_ORDER_ID=:o',l=legacy,o=s['order_id'])
 s.update(legacy_order_id=int(legacy),legacy_pallet_id=int(pallet),logistics_values='SYNTHETIC_BOX_10EA_1.2KG_0.024M3');save()
print(json.dumps({k:s[k]for k in ['warehouse_id','case_id','legacy_order_id','legacy_pallet_id','st_pallet','origin']}))
