"""Recipient forecast gates and competing native holds on the owned program warehouse.

Uses ASGI HTTP with real RUSERS/Oracle, not TCP or an external ERP. The receipt runner
may continue independently: this check changes only its own documents/holds, then
releases them and cancels its synthetic main order. No stock is inserted.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
os.environ['WMS_ADMIN_AUTH_ENABLED'] = '1'
os.environ['WMS_API_AUDIT_LOCAL_DIR'] = str(ROOT/'api/wms_api_server/runtime/api_audit/forecast-acceptance')
sys.path[:0] = [str(ROOT/'api/wms_api_server'), str(Path(__file__).parent)]
import live_program_orders as program
from fastapi.testclient import TestClient
from app.main import app

OUT = program.q.OUT/'forecast-acceptance'
FILE = OUT/'state.json'
s = json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else dict(steps={}, calls=[], checks=[])
W = program.s['fixture']['warehouse_id']
BASE = f'/api/tradecase/warehouses/{W}'
TAG = 'FG27.'+program.s['fixture']['tag']
client = TestClient(app)


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    temporary=FILE.with_suffix('.tmp');temporary.write_text(json.dumps(s,default=str),encoding='utf-8');temporary.replace(FILE)


def http(path, body):
    started=time.perf_counter();response=client.post(path,json=body,auth=('admin','admin123'))
    value=response.json()
    s['calls'].append(dict(path=path,status=response.status_code,elapsed_ms=round((time.perf_counter()-started)*1000,2),body=body,result=value))
    return response.status_code,value


def step(key,path,body,status=200,code=None):
    if key not in s['steps']:s['steps'][key]=dict(path=path,body=body,status=status);save()
    record=s['steps'][key]
    if 'result' not in record:
        actual,value=http(record['path'],record['body']);save()
        assert actual==record['status'],(key,actual,value)
        record['result']=value;save()
    if code:assert record['result']['detail']['code'].startswith(code),record
    return record['result']


def send(key,kind,identifier,payload,version=1):
    return step(key,'/api/tradecase/messages',dict(schema_version=1,event_id=TAG+'.'+key,source_id='TC03.SAP',warehouse_id=W,document_id=identifier,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type=kind,**payload)))


def run():
    assert s.get('status')!='CLOSED','Never reopen closed proof'
    own=program.q.db("select nvl(sum(h.BASE_QTY),0)from RRL_TRADE_TOPUP_HOLD h join RRL_TRADE_TOPUP_PROPOSAL p on p.PROPOSAL_ID=h.PROPOSAL_ID where p.WARE_ID=:w and p.TRIP_ID in('T.FORECAST.1','T.FORECAST.2')and h.STATUS='ACTIVE'",w=W)[0][0]
    assert W==210069361 and program.q.stock()[1]==own,'No other hold may be changed'
    departure=program.s['day']+'T12:00:00+03:00'
    profile=step('vehicle','/api/admin/transport/vehicles',dict(num_plat=TAG,transtype_id='10',max_weight_kg=20,max_pallets=2,sobstvennyy=True),status=201)
    vid=profile['id']
    if 'vehicle.profile' not in s['steps']:
        response=client.get(f'/api/admin/transport/vehicles/{vid}/profile',auth=('admin','admin123'));assert response.status_code==200
        p=response.json()
        step('vehicle.profile','/api/admin/transport/vehicle-profiles',dict(operation_id=TAG+'.profile',vehicle_id=vid,expected_source_hash=p['base_hash'],expected_version=p['version'],vehicle_size_class='QA_FORECAST',cargo_length_mm=1000,cargo_width_mm=500,cargo_height_mm=500,outer_height_mm=1500,outer_length_mm=2000,floor_variants=[dict(code='TWO',limits=[dict(pallet_type_id=35,max_places=2)])],reason='Owned two-box forecast proof',evidence_reference='TEST_NOT_HARDWARE'))
    recipient=dict(title='Forecast gate proof',target_owner_id='SNS',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0,topup_enabled=False,topup_horizon_days=2)
    send('recipient.off','RECIPIENT','C.FORECAST',recipient)
    order=dict(recipient_id='C.FORECAST',planned_ship_at=departure,lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='1',uom='BOX',min_osg_days=0)])
    send('main','ORDER','O.FORECAST',order)
    trip=dict(vehicle_id=TAG,planning_source='SAP',planned_departure_at=departure,capacity_kg='20',capacity_m3='0.2',orders=[dict(order_id='O.FORECAST',line_id='1',quantity='1')])
    send('T.FORECAST.1','TRIP','T.FORECAST.1',trip)
    send('main.second','ORDER','O.FORECAST.2',order)
    send('trip.second.current','TRIP','T.FORECAST.2',dict(trip,orders=[dict(order_id='O.FORECAST.2',line_id='1',quantity='1')]))
    day=datetime.fromisoformat(program.s['day']+'T00:00:00+03:00')
    need=dict(recipient_id='C.FORECAST',sku_id='A',recipient_version=1,sku_version=1,forecast_kind='MOVEMENT',snapshot_at=datetime.now(timezone.utc).isoformat(),period_from=day.isoformat(),period_until=(day+timedelta(days=2)).isoformat(),uom='BOX',forecast_quantity='3',target_quantity='0',available_quantity='0',received_in_available=True,supplies=[dict(supply_id=key,version=1,quantity='1',uom='BOX',status='PLANNED',confirmed=True,current_trip=key=='O.FORECAST',expected_at=departure)for key in ['O.FORECAST','O.FORECAST.2']])
    send('need.off','NEED','N.FORECAST',need)
    route=BASE+'/trips/T.FORECAST.1'
    preview=dict(need_ids=['N.FORECAST'],max_age_minutes=1440)
    step('missing',route+'/topup-preview',dict(preview,need_ids=['N.MISSING']),404,'NEED_SOURCE_MISSING')
    step('off',route+'/topup-preview',preview,409,'TOPUP_RECIPIENT_DISABLED')
    recipient['topup_enabled']=True;send('recipient.on','RECIPIENT','C.FORECAST',recipient,2)
    step('stale',route+'/topup-preview',preview,409,'NEED_MASTER_VERSION_CHANGED')
    need['recipient_version']=2;send('need.on','NEED','N.FORECAST',need,2)
    send('legacy','NEED','N.FORECAST.CONSUMPTION',dict(need,forecast_kind='CONSUMPTION'))
    step('consumption',route+'/topup-preview',dict(preview,need_ids=['N.FORECAST.CONSUMPTION']),409,'TOPUP_MOVEMENT_FORECAST_REQUIRED')
    send('wide','NEED','N.FORECAST.WIDE',dict(need,period_until=(day+timedelta(days=3)).isoformat()))
    step('wide.denial',route+'/topup-preview',dict(preview,need_ids=['N.FORECAST.WIDE']),409,'TOPUP_RECIPIENT_HORIZON_EXCEEDED')
    send('zero','NEED','N.FORECAST.ZERO',dict(need,forecast_quantity='2'))
    assert step('zero.preview',route+'/topup-preview',dict(preview,need_ids=['N.FORECAST.ZERO']))['proposed_boxes']==0
    p=step('save.old',route+'/topup-proposals',dict(preview,operation_id=TAG+'.save.old'))['proposals'][0]
    send('recipient.disable','RECIPIENT','C.FORECAST',dict(recipient,topup_enabled=False),3)
    step('disabled.confirm',route+f"/topup-proposals/{p['proposal_id']}/confirm",dict(operation_id=TAG+'.disabled.confirm',expected_version=p['version']),409,'TOPUP_RECIPIENT_DISABLED')
    assert program.q.stock()[1]==0
    send('recipient.restore','RECIPIENT','C.FORECAST',recipient,4)
    need['recipient_version']=4;send('need.restore','NEED','N.FORECAST',need,3)
    compete(preview)
    for index,order_id in [(1,'O.FORECAST'),(2,'O.FORECAST.2')]:
        send('trip.cancel.'+str(index),'TRIP',f'T.FORECAST.{index}',dict(trip,cancelled=True,orders=[dict(order_id=order_id,line_id='1',quantity='1')]),2)
    send('cancel.main.fixed','ORDER','O.FORECAST',dict(order,cancelled=True),2)
    send('cancel.main.second','ORDER','O.FORECAST.2',dict(order,cancelled=True),2)
    send('recipient.close','RECIPIENT','C.FORECAST',dict(recipient,topup_enabled=False),5)
    assert program.q.stock()[1]==0
    assert program.q.db("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
    if s.get('error'):s.setdefault('previous_errors',[]).append(s.pop('error'))
    s.update(status='CLOSED',scope='ASGI HTTP / real Oracle; not TCP, ERP or physical dispatch',hard_after=0);save()


def compete(preview):
    if 'race.requests' not in s:
        requests=[]
        for index in (1,2):
            route=BASE+f'/trips/T.FORECAST.{index}'
            p=step('save.current.'+str(index),route+'/topup-proposals',dict(preview,operation_id=TAG+'.save.'+str(index)))['proposals'][0]
            assert p['approved_boxes']==1,p
            requests.append(dict(path=route+f"/topup-proposals/{p['proposal_id']}/confirm",body=dict(operation_id=TAG+'.confirm.'+str(index),expected_version=p['version']),proposal_id=p['proposal_id'],route=route))
        s['race.requests']=requests;save()
    if 'race.results' not in s:
        with ThreadPoolExecutor(max_workers=2)as pool:
            results=list(pool.map(lambda r:http(r['path'],r['body']),s['race.requests']))
        s['race.results']=results;save()
    assert sorted(x[0]for x in s['race.results'])==[200,409],s['race.results']
    loser=next(i for i,r in enumerate(s['race.results'])if r[0]==409)
    assert s['race.results'][loser][1]['detail']['code']=='TRADE_TOPUP_NEED_ALREADY_COVERED'
    winner=next(i for i,r in enumerate(s['race.results'])if r[0]==200);request=s['race.requests'][winner]
    if 'released' not in s['steps']:
        assert program.q.stock()[1]==10
        actual,replay=http(request['path'],request['body']);assert actual==200 and replay==s['race.results'][winner][1]
    result=s['race.results'][winner][1]
    step('released',request['route']+f"/topup-proposals/{request['proposal_id']}/release",dict(operation_id=TAG+'.release',expected_version=result['version']))
    refused=s['race.requests'][loser]
    step('reject.loser',refused['route']+f"/topup-proposals/{refused['proposal_id']}/decision",dict(operation_id=TAG+'.reject',expected_version=refused['body']['expected_version'],action='REJECT'))


if __name__=='__main__':
    try:
        run();print(json.dumps(dict(status=s['status'],calls=len(s['calls']),hard=s['hard_after'])))
    except Exception as error:
        s['error']=str(error);save();raise
