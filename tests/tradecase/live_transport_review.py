"""Real native review checks; injected document/task metadata is rolled back, never stock-seeded."""
from pathlib import Path
import json,os,sys,hashlib
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
import oracledb
P=Path('runtime/test-evidence/tradecase/2026-10-19/T07/review-native.json');s=dict(status='RUNNING',checks=[],metadata_injection='ROLLBACK_ONLY_NO_PHYSICAL_WRITES')
def read(q):
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc('RRL_TRADE_STOCK_API.execute_command',[215590763,'admin',json.dumps(dict(command_type='TRIP_STATE',trip_id='R1.1156')),'[]',out]);r=out.getvalue();return r if isinstance(r,dict)else json.loads(r.read()if hasattr(r,'read')else r)
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  baseline=read(q);assert baseline['basis_current']and baseline['document_ready'];s['baseline']=baseline
  # Change the source SKU through its real native receiver in this transaction, then roll it back.
  q.execute("select BODY_JSON,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=215590763 and ENTITY_TYPE='SKU'and EXTERNAL_ID='A'");payload,version=q.fetchone();payload=payload if isinstance(payload,dict)else json.loads(payload.read())
  wire=dict(schema_version=1,event_id='T7.REVIEW.SKU.NEXT',source_id='TC03.SAP',warehouse_id=215590763,document_id='A',version=version+1,occurred_at='2026-10-19T14:45:00+03:00',payload=payload)
  encode=lambda x:json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':'))
  raw=encode(wire);business={k:wire[k]for k in ['schema_version','source_id','warehouse_id','document_id','version','payload']};wire['payload_hash']=hashlib.sha256(raw.encode()).hexdigest();wire['business_hash']=hashlib.sha256(encode(business).encode()).hexdigest()
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc('RRL_TRADE_DOCUMENT_API.receive_document',[215590763,'admin',encode(wire),out]);r=out.getvalue();r=r if isinstance(r,dict)else json.loads(r.read()if hasattr(r,'read')else r);assert r['status']=='ACCEPTED',r
  stale=read(q);assert stale['basis_current']is False and stale['document_ready']is False;s['stale_binding']=stale;s['checks'].append('existing_binding_stale_not_404_after_source_revision')
  c.rollback();assert read(q)==baseline;s['checks'].append('source_revision_and_outbox_rollback_restores_baseline')
  # Add one unlisted FULL_PALLET line to the same native ST using only owned logical QA metadata.
  q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY,CREATED_BY)select RRL_PICK_TASK_SQ.nextval,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,'FULL_PALLET','DONE',ARTICUL,'690000000312355716',SOURCE_CELL_CODE,TARGET_CELL_CODE,1,'admin'from RRL_PICK_TASK where PICK_TASK_ID=2166");assert q.rowcount==1
   q.execute("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM,CREATED_BY,PICKED_PALLET_UID)values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,2185,641539,'TC7.PALLET.1156','TRADECASE.QA.1156','PICKED',1,0,'QA_REVIEW_ROLLBACK','admin','690000000312355716')")
   unlisted=read(q);assert unlisted['basis_current']is False and unlisted['document_ready']is False;s['unlisted_full_pallet']=unlisted;s['checks'].append('unlisted_full_pallet_invalidates_trip_admission')
   c.rollback()
  finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
  assert read(q)==baseline;s['checks'].append('full_pallet_fault_rollback_restores_baseline')
  for load in ['T7.LOAD.1155','T7.LOAD.1156']:q.callproc('RRL_TRADE_TRANSIT_PROOF.assert_load',[load,215590763]);s['checks'].append('exact_original_unit_fingerprint_'+load)
  try:q.callproc('RRL_TRADE_TRANSIT_PROOF.assert_load',['T7.LOAD.1156',211559882]);raise AssertionError('foreign load admitted')
  except oracledb.DatabaseError as e:assert e.args[0].code==20886
  q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=215590763');assert list(q.fetchone())==[110,0]
  q.execute("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'");assert q.fetchone()[0]==0
 s['status']='PASS';print(json.dumps(dict(status=s['status'],checks=s['checks'])))
except Exception as e:s['status']='FAIL';s['error']=str(e);raise
finally:s['http']=CALLS;P.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
