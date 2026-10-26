"""Close only the owned corrected 660 BOX physical fixture through composition, native departure and wave finish."""
import json,os,re,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).parent))
import live_topup_physical_660 as qa
qa.s.update(json.loads(qa.STATE.read_text(encoding='utf-8')));s=qa.s
PROOF=qa.OUT/'topup-physical-660-close.json'
def setup():
 assert s['fixture']['warehouse_id']==223214750 and s['phase']!='CLOSED'
 os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[\x60,)\s]',Path('AGENTS.md').read_text(encoding='utf-8'))[1]
 p=json.loads(PROOF.read_text());assert p['phase']=='LOADED' and p['load_posted']==6600
 assert tuple(qa.stock())==(0,0,0)
def prepare():
 setup();w=s['fixture']['warehouse_id'];t=s['transport'];s['phase']='LOADED_FOR_DEPARTURE';s['active_close_cycle']=PROOF.name;qa.save()
 base=f'/api/tradecase/warehouses/{w}'
 if 'closing_trip_version'not in s:
  previous=max((v['body']for v in s['steps'].values()if isinstance(v,dict)and v.get('body')and v['body'].get('document_id')=='T1'),key=lambda b:b['version'])
  payload=dict(previous['payload']);payload.pop('entity_type',None);payload['capacity_m3']='85.8'
  s['closing_trip_version']=previous['version']+1;s['closing_trip_payload']=payload
  s['closing_fixture_correction']='Owned synthetic body 13.2x2.5x2.6m (85.8m3); original 66m3 pallet interpretation remains unaccepted'
  qa.save()
 qa.send('closing_trip','TRIP','T1',s['closing_trip_payload'],version=s['closing_trip_version'])
 for order,qty in [('O1',6000),('O.FULL600.V2',600)]:
  key='closing.composition.'+order
  card=qa.step(key,'POST','/api/tradecase/order-compositions/report',dict(warehouse_id=w,order_id=order));assert card['units']==card['codes']==qty,(order,card)
  for system,sender in [('SAP','TC03.SAP'),('SKM','TC03.SKM')]:
   qa.step(key+'.'+system,'POST','/api/tradecase/order-compositions/acknowledgments',dict(schema_version=1,warehouse_id=w,order_id=order,system_code=system,sender_id=sender,event_id=qa.tag()+'.'+key+'.'+system,composition_no=card['composition_no'],signature=card['signature'],outcome='ACCEPTED',occurred_at=datetime.now(timezone.utc).isoformat()))
 path=base+'/trips/T1'
 qa.step('closing.binding','POST',path+'/binding',dict(operation_id=qa.tag()+'.closing.bind',native_task_id=t['transport_task_id'],expected_trip_version=s['closing_trip_version'],expected_binding_version=0))
 if 'closing.document'not in s['steps']:
  state=qa.expect(200,qa.http('GET',path+'/execution'))
  qa.step('closing.document','POST',path+'/transport-document',dict(operation_id=qa.tag()+'.closing.doc',source_id='TC03.SAP',external_event_id=qa.tag()+'.closing.doc',expected_trip_version=s['closing_trip_version'],expected_binding_version=1,document_version=1,document_status='READY',external_document_id='TEST_NOT_INDUSTRIAL_660_'+s['fixture']['tag'],manifest_signature=state['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat()))
 s['phase']='DOCUMENT_READY';qa.save()
def depart():
 setup();trip=s['transport']['transport_task_id']
 answer=qa.step('closing.depart','POST',f'/api/transport/loading/{trip}/depart',dict(operation_id=qa.tag()+'.closing.depart'))
 assert qa.expect(200,qa.http('POST',f'/api/transport/loading/{trip}/depart',s['steps']['closing.depart']['body']))==answer
 s['closing_departure_facts']=[list(x)for x in qa.db("select STATUS,count(*),sum(GROSS_WEIGHT_KG),sum(BOUNDING_VOLUME_M3)from RRL_TT_HU_LOAD_FACT where TT_ID=:t and STATUS='DEPARTED'group by STATUS",t=trip)]
 assert s['closing_departure_facts']==[['DEPARTED',33,6600,79.2]],s['closing_departure_facts']
 s['phase']='DEPARTED';qa.save()
def finish():
 setup()
 for key in ['main_wave_id','topup_proven_retry_wave_id']:
  wave=s[key]
  if 'closing.finish.'+key not in s['steps']:
   p=qa.expect(200,qa.http('GET',f'/api/picking/waves/{wave}/execution'));assert p['ready'],p
  qa.step('closing.finish.'+key,'POST',f'/api/picking/waves/{wave}/finish-execution',dict(operation_id=qa.tag()+'.closing.finish.'+key))
 assert qa.db("select STATUS,count(*)from RRL_PICK_WAVE where PICK_WAVE_ID in(:a,:b)group by STATUS",a=s['main_wave_id'],b=s['topup_proven_retry_wave_id'])==[('DONE',2)]
 s['closing_fulfillment']=[list(x)for x in qa.db("select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID in(:a,:b)group by STATUS",a=s['native_main']['order'],b=s['native_topup_matched']['order'])]
 assert s['closing_fulfillment']==[['SHIPPED',33,6600]],s['closing_fulfillment']
 assert qa.db("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
 with qa.oracle_connection()as c:
  q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'and WARE_ID=:w",a=s['fixture']['actor'],w=s['fixture']['warehouse_id']);assert q.rowcount==1
  q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a and REVOKED_AT is null',a=s['fixture']['role']);c.commit()
 s['closing_stock']=qa.stock();assert tuple(s['closing_stock'])==(0,0,0)
 s['closing_slow_sql']=[list(x)for x in qa.db('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:n order by ELAPSED_MS desc fetch first 25 rows only',n=s['fixture']['slow_marker'])]
 s['phase']='CLOSED';s['closing_status']='PASS';s['closing_providers']='SYNTHETIC_SAP_SKM_AND_MANUAL_MEASUREMENTS';qa.save()
def main():
 try:globals()[sys.argv[1]]();print(json.dumps(dict(phase=s['phase'],stock=qa.stock())))
 finally:s.setdefault('http',[]).extend(qa.CALLS);qa.save()
if __name__=='__main__':main()
