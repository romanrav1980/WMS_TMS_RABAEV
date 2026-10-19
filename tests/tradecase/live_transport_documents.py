"""Synthetic ERP business results gate real native departure, independently of message receipt."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path(os.environ.get('TRADECASE_TRANSPORT_FIXTURE',str(ROOT/'runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1155.json')));s=json.loads(P.read_text());w=s['warehouse_id'];tag=str(s['case_id']);trip='R1.'+tag;base=f'/api/tradecase/warehouses/{w}/trips/{trip}'
def save():P.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def replay_equal(new,old):assert new['replayed']and {k:v for k,v in new.items()if k!='replayed'}=={k:v for k,v in old.items()if k!='replayed'}
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 if 'external_trip'not in s:
  body=dict(schema_version=1,event_id='T7.TRIP.'+tag,source_id='TC03.SAP',warehouse_id=w,document_id=trip,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type='TRIP',vehicle_id=s['vehicle_number'],planning_source='SAP',planned_departure_at='2026-11-01T10:00:00+03:00',capacity_kg='1000',capacity_m3='17.28',orders=[dict(order_id=s.get('demand_order_id','AFTER'),line_id='1',quantity=str(s.get('quantity',100)))]))
  s['external_trip']=expect(200,http('POST','/api/tradecase/messages',body));save()
 if 'trip_binding'not in s:
  s['trip_bind_body']=dict(operation_id='T7.TRIP.BIND.'+tag,native_task_id=s['transport_task_id'],expected_trip_version=1,expected_binding_version=0);save()
  s['trip_binding']=expect(200,http('POST',base+'/binding',s['trip_bind_body']));save()
 replay_equal(expect(200,http('POST',base+'/binding',s['trip_bind_body'])),s['trip_binding'])
 if 'business_error'not in s:
  state=expect(200,http('GET',base+'/execution'));assert not state['document_ready']and state['document_status']=='MISSING',state
  s['error_body']=dict(operation_id='T7.DOC.ERROR.'+tag,source_id='TC03.SAP',external_event_id='T7.DOC.ERROR.'+tag,expected_trip_version=1,expected_binding_version=1,document_version=1,document_status='ERROR',manifest_signature=state['manifest_signature'],error_reason='QA simulated ERP business error after successful delivery',occurred_at=datetime.now(timezone.utc).isoformat());save()
  s['business_error']=expect(200,http('POST',base+'/transport-document',s['error_body']));assert s['business_error']['document_status']=='ERROR';save()
 replay_equal(expect(200,http('POST',base+'/transport-document',s['error_body'])),s['business_error'])
 if 'error_blocks_departure'not in s:
  s['error_blocks_departure']=expect(409,http('POST',f"/api/transport/loading/{s['transport_task_id']}/depart",dict(operation_id='T7.DEPART.ERROR.'+tag)));assert 'DOCUMENT_NOT_READY'in s['error_blocks_departure']['detail']['message'];save()
 if 'ready_body'not in s:
  state=expect(200,http('GET',base+'/execution'));assert not state['document_ready']
  s['ready_body']=dict(operation_id='T7.DOC.READY.'+tag,source_id='TC03.SAP',external_event_id='T7.DOC.READY.'+tag,expected_trip_version=1,expected_binding_version=1,document_version=2,document_status='READY',external_document_id='TEST_TRANSPORT_DOC_'+tag,manifest_signature=state['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat());save()
 if 'ready_result'not in s:
  bad=dict(s['ready_body'],operation_id='T7.DOC.BADHASH.'+tag,external_event_id='T7.DOC.BADHASH.'+tag,manifest_signature='A'*64);expect(409,http('POST',base+'/transport-document',bad))
  s['ready_result']=expect(200,http('POST',base+'/transport-document',s['ready_body']));save()
 state=expect(200,http('GET',base+'/execution'));assert state['document_ready'],state;s['transport_state']=state
 if 'departed'not in s:
  s['depart_body']=dict(operation_id='T7.DEPART.'+tag);save();s['departed']=expect(200,http('POST',f"/api/transport/loading/{s['transport_task_id']}/depart",s['depart_body']));save()
 assert expect(200,http('POST',f"/api/transport/loading/{s['transport_task_id']}/depart",s['depart_body']))==s['departed']
 with oracle_connection()as c:
  q=c.cursor();q.execute('select STATUS,DEPARTURE_OPERATION_ID,DEPARTED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o',o=s['load_body']['operation_id']);status,operation,at=q.fetchone();assert status=='DEPARTED'and operation==s['depart_body']['operation_id'];s['departed_at']=str(at)
  q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);assert list(q.fetchone())==[s.get('expected_remaining',150),0]
 s['transport_stage']='PASS';s['provider']='LOCAL_SYNTHETIC_ONLY';print(json.dumps(dict(status=s['transport_stage'],trip=s['transport_task_id'],departure=s['departed'],provider=s['provider'])))
finally:s['http']+=CALLS;save()
