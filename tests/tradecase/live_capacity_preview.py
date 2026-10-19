"""Actual Oracle/API plan capacity on isolated metadata; no 660-box shipment claim."""
from pathlib import Path
from datetime import datetime,timezone
from uuid import uuid4
import json,os,sys,secrets
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
from live_stock_acceptance import setup
P=Path('runtime/test-evidence/tradecase/2026-10-19/T08');P.mkdir(parents=True,exist_ok=True);F=P/'capacity-fixture.json';s=json.loads(F.read_text())if F.exists()else dict(status='RUNNING',history=[])
def save():F.write_text(json.dumps(s,indent=2,default=str))
def send(kind,identity,payload,version=1):return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id='T8.'+identity+'.'+str(version),source_id='TC03.SAP',warehouse_id=s['a']['warehouse_id'],document_id=identity,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**payload))))
def profile(length,version):
 v=s['vehicle'];base=expect(200,http('GET',f'/api/admin/transport/vehicles/{v}/profile'))
 body=dict(operation_id='T8.profile.'+str(v)+'.'+str(version),vehicle_id=v,expected_source_hash=base['base_hash'],expected_version=base['version'],vehicle_size_class='QA_BODY_T8',cargo_length_mm=length,cargo_width_mm=2500,cargo_height_mm=2000,outer_height_mm=3000,outer_length_mm=14000,floor_variants=[dict(code='QA33EURO',limits=[dict(pallet_type_id=1,max_places=33)])],reason='Synthetic source acceptance body geometry, not a road measurement',evidence_reference='TEST_SOURCE_T8_ONLY')
 return expect(200,http('POST','/api/admin/transport/vehicle-profiles',body))
def run():
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 for key in ['a','b']:
  if key not in s:
   f=setup();f.pop('password');s[key]=f;save()
 w=s['a']['warehouse_id'];base=f'/api/tradecase/warehouses/{w}'
 if 'prepared'not in s:
  with oracle_connection()as c:
   q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
   try:
    for key in ['a','b']:q.execute('update RRL_ARTICULS set COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=10,DIMKOR_X=0.4,DIMKOR_Y=0.5,DIMKOR_Z=0.5 where ACTICUL=:a',a=s[key]['article'])
    c.commit()
   finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  expect(200,http('PUT',base+'/site',dict(operation_id='T8.site.'+str(w),expected_version=0,source_id='TC03.SAP',active_skm='TC03.SKM',planning_source='SAP',enabled=True,reason='Isolated read-only capacity acceptance')))
  for owner in ['SNS','BLC']:send('OWNER',owner,dict(title=owner))
  for sku,key,mrc in [('A','a','200'),('B','b','220')]:send('SKU',sku,dict(title='QA source '+sku,wms_article_id=s[key]['article'],units_per_box=10,permitted_mrc=[mrc]))
  for i in range(1,4):send('RECIPIENT','C'+str(i),dict(title='QA C'+str(i),target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='IN_TRANSIT',min_osg_days=0,lead_time_days=0))
  for number,recipient,sku,mrc,quantity in [('O101','C1','A','200','200'),('O102','C2','A','200','150'),('O103','C3','B','220','250')]:send('ORDER',number,dict(recipient_id=recipient,planned_ship_at='2026-11-01T10:00:00+03:00',lines=[dict(line_id='1',sku_id=sku,source_owner_id='SNS',target_owner_id='BLC',mrc=mrc,quantity=quantity,uom='BOX',min_osg_days=0)]))
  s['prepared']=True;save()
 if 'vehicle'not in s:s['plate']='TC8QA'+s['a']['tag'];s['vehicle']=expect(201,http('POST','/api/admin/transport/vehicles',dict(num_plat=s['plate'],transtype_id='10',max_weight_kg=8000,max_pallets=33,sobstvennyy=True)))['id'];save()
 if 'profile1'not in s:s['profile1']=profile(13200,1);save()
 def trip(kg,volume):return dict(vehicle_id=s['plate'],planning_source='SAP',planned_departure_at='2026-11-01T10:00:00+03:00',capacity_kg=str(kg),capacity_m3=str(volume),orders=[dict(order_id=o,line_id='1',quantity=q)for o,q in [('O101','200'),('O102','150'),('O103','250')]])
 if 'trips'not in s:
  send('TRIP','TC8.R1',trip(8000,66));s['trips']=True;save()
 path=base+'/trips/TC8.R1/capacity?sku_id=A&requested_boxes='
 if 'initial'not in s:
  s['initial']=expect(200,http('GET',path+'60'));assert s['initial']['fitting_boxes']==60 and s['initial']['maximum_boxes']==60 and s['initial']['operational_admission']is False
  s['partial']=expect(200,http('GET',path+'80'));assert [s['partial'][k]for k in ['fitting_boxes','remaining_boxes']]==[60,20]
  send('TRIP','TC8.R1',trip(6200,66),2);s['mass']=expect(200,http('GET',path+'60'));assert s['mass']['fitting_boxes']==20;save()
 if 'profile2'not in s:s['profile2']=profile(12800,2);send('TRIP','TC8.R1',trip(8000,64),3);save()
 s['smaller']=expect(200,http('GET',path+'60'));assert s['smaller']['fitting_boxes']==40 and s['smaller']['remaining_boxes']==20
 with oracle_connection()as c:
  q=c.cursor();actor='T8R'+uuid4().hex[:8];password=secrets.token_hex(24);s['scope_actor']=actor
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'QA capacity reader','TC03QA',:w,0,1)",a=actor,p=password,w=w)
  q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:r,'QA capacity reader',1,1)",r=actor)
  q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,'tradecase_view')",r=actor)
  q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:r,:r,:r,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','QA capacity view acceptance',1)",r=actor,w=str(w));c.commit();save()
 expect(403,http('GET',path+'60',actor=s['scope_actor'],password=password))
 grant=dict(operation_id='T8.owner.'+s['scope_actor'],expected_version=0,username=s['scope_actor'],owner_id='SNS',can_view=True,can_operate=False,reason='Source party view for capacity, no mutation rights')
 expect(200,http('PUT',base+'/stock/owner-grants',grant));assert expect(200,http('GET',path+'60',actor=s['scope_actor'],password=password))==s['smaller']
 s['departed_blocked']=expect(200,http('GET','/api/tradecase/warehouses/215590763/trips/R1.1156/capacity?sku_id=A&requested_boxes=60'));assert s['departed_blocked']['maximum_boxes']is None and s['departed_blocked']['blocking_reason']=='LOAD_ALREADY_STARTED'
 with oracle_connection()as c:
  q=c.cursor();q.execute('select count(*)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0',w=w);assert q.fetchone()[0]==0
 s['status']='PASS';s['limits']='PLAN_PREVIEW_ONLY; no physical stock, allocation, dispatcher approval or provider exchange';s.pop('error',None);print(json.dumps(dict(status=s['status'],warehouse_id=w,initial=s['initial']['fitting_boxes'],partial_remaining=s['partial']['remaining_boxes'],smaller=s['smaller']['fitting_boxes'],mass=s['mass']['fitting_boxes'])))
if __name__=='__main__':
 try:run()
 except Exception as e:s['status']='FAIL';s['error']=str(e);raise
 finally:
  with oracle_connection()as c:
   q=c.cursor()
   for key in ['a','b']:
    if key in s:q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=s[key]['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=s[key]['role'])
   if 'scope_actor'in s:
    q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=s['scope_actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r',r=s['scope_actor'])
   c.commit()
  s['history']+=CALLS;save()
