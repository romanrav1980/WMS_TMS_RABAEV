"""Own existing outbox: disabled preserves pending; explicit mock never creates legal ACK."""
import json,sys,os
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.integrations.public import MockRegulatoryAdapter,build_regulatory_adapter
from app.services.outbox_service import OutboxService
s=get_settings();tag=uuid4().hex[:10];target='QA131_'+tag.upper();admin=httpx.Client(auth=('admin','admin123'),timeout=35)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 event=int(q.callfunc('RRL_TRACEABILITY_API.enqueue_event',oracledb.DB_TYPE_NUMBER,keyword_parameters={'p_event_type':'QA_SIMULATION_ONLY','p_aggregate_type':'PALLET','p_aggregate_id':'TOBACCO.CONTEXT:fe13c21d8c','p_idempotency_key':'QA131:'+tag,'p_payload_json':json.dumps({'synthetic':True,'stock_changed':False,'government_ack':False}),'p_target_system':target,'p_correlation_id':'QA131:'+tag}));c.commit()
 prior={key:os.environ.get(key)for key in ['NICORA_REGULATORY_MODE','NICORA_ALLOW_REGULATORY_MOCK']}
 try:
  for key in prior:os.environ.pop(key,None)
  result=OutboxService(OracleGateway()).process_next('QA131:'+tag,target);assert result['status']=='NOT_CONFIGURED' and result['pending_events_preserved'] and result['real_external_ack'] is False
  q.execute('select STATUS,TRY_COUNT from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id',id=event);assert q.fetchone()==('PENDING',0)
  q.execute('select count(*)from RRL_ADAPTER_REQUEST_LOG where EVENT_OUTBOX_ID=:id',id=event);assert q.fetchone()[0]==0
  os.environ['NICORA_REGULATORY_MODE']='REAL';assert build_regulatory_adapter().configured is False
  os.environ['NICORA_REGULATORY_MODE']='MOCK';assert build_regulatory_adapter().configured is False
  os.environ['NICORA_ALLOW_REGULATORY_MOCK']='1';assert build_regulatory_adapter().simulated is True
  explicit=OutboxService(OracleGateway(),MockRegulatoryAdapter()).process_next('QA131:'+tag,target)
  assert explicit['status']=='DONE' and explicit['external_status']=='SIMULATED_ACCEPTED' and explicit['simulation'] and not explicit['real_external_ack'],explicit
  q.execute('select SIGNATURE_STATUS,EXTERNAL_STATUS,EXTERNAL_DOCUMENT_ID from RRL_ADAPTER_REQUEST_LOG where EVENT_OUTBOX_ID=:id',id=event);signature,status,document=q.fetchone();assert signature=='MOCK_NOT_SIGNED' and status=='SIMULATED_ACCEPTED' and document.startswith('MOCK-')
  r=admin.get(f'http://127.0.0.1:8088/api/admin/adapter-requests?event_outbox_id={event}');assert r.status_code==200,r.text
  rows=r.json();assert len(rows)==1 and rows[0]['simulation']and rows[0]['external_ack_verified']is False and rows[0]['acknowledgment_kind']=='SIMULATED',rows
  r=admin.get('http://127.0.0.1:8088/api/integrations/regulatory/runtime');assert r.status_code==200,r.text;assert r.json()['real_external_ack']is False
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA='TOBACCO.CONTEXT:fe13c21d8c'");assert q.fetchone()==(3,0)
  print('PASS131 defaultdisabled pending/try0/log0, unsupportedREAL and unapprovedMOCK disabled; explicitMOCK own event '+str(event)+' SIMULATED_ACCEPTED/no external legalACK/API evidence/stock3 unchanged',flush=True)
 finally:
  for key,value in prior.items():
   if value is None:os.environ.pop(key,None)
   else:os.environ[key]=value
