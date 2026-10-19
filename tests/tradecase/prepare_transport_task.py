"""Owned transport master data and trip through current API, resumable by saved IDs."""
from pathlib import Path
import json,os,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path(os.environ.get('TRADECASE_TRANSPORT_FIXTURE',str(ROOT/'runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1155.json')));s=json.loads(P.read_text());base='/api/admin/transport';s.setdefault('vehicle_number','TC7QA1155');s.setdefault('dock','TC7D1155')
def save():P.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute('select count(*)from RRL_TT_DOCK where DOCK=:d',d=s['dock'])
  if q.fetchone()[0]==0:
   q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
   try:
    q.execute('insert into RRL_TT_DOCK(DOCK,WARE_ID,ORD,COUNT_OF_PALLETS,DOCK_IS_BLOCKED)values(:d,:w,1,10,0)',d=s['dock'],w=s['warehouse_id']);c.commit()
   finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 if 'vehicle_id'not in s:s['vehicle_id']=expect(201,http('POST',base+'/vehicles',dict(num_plat=s['vehicle_number'],transtype_id='10',max_weight_kg=1000,max_pallets=10,sobstvennyy=True)))['id'];save()
 if 'driver_id'not in s:s['driver_id']=expect(201,http('POST',base+'/drivers',dict(name='TRADECASE QA driver1155',license_number='TEST_NOT_ROAD_1155')))['id'];save()
 if 'transport_task_id'not in s:s['transport_created']=expect(200,http('POST',base+'/tasks',dict(transtype='10',shipment_date='2026-11-01')));s['transport_task_id']=s['transport_created']['task_id'];save()
 if 'trip_configured'not in s:s['trip_configured']=expect(200,http('PATCH',base+'/tasks/'+str(s['transport_task_id']),dict(transport=s['vehicle_number'],voditel_id=s['driver_id'],dock=s['dock'],shipment_time='10:00',primechanie='TRADECASE isolated QA1155, no real dispatch')));save()
 if 'assigned'not in s:s['assigned']=expect(200,http('POST',base+'/tasks/'+str(s['transport_task_id'])+'/sts',dict(st_numbers=[s['st_number']])));save()
 s['vehicle_profile']=expect(200,http('GET',base+'/vehicles/'+str(s['vehicle_id'])+'/profile'));print(json.dumps(dict(trip=s['transport_task_id'],vehicle=s['vehicle_id'],profile=s['vehicle_profile']),default=str))
finally:s['http']+=CALLS;save()
