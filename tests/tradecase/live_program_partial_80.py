"""Program section 8: one 80 BOX order, 60 BOX dispatched, 20 retained with exact codes and holds.

Four owned pallets of 20 BOX (200 EA). Real HTTP/Oracle writers; ERP/marking replies and dimensions are synthetic.
The retained pallet is dispatched separately only after the intermediate 80/80/60/20 evidence is saved.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import live_topup_physical_660 as qa
from full_pallet_fixture import prepare_shipment

qa.OUT = qa.ROOT / 'runtime/test-evidence/tradecase/2026-10-26/T08/partial-80'
qa.STATE = qa.OUT / 'state.json'
qa.PALLETS = qa.MAIN_PALLETS = 4
if qa.STATE.exists():
    qa.s.update(json.loads(qa.STATE.read_text(encoding='utf-8')))
s = qa.s


def prepare():
    f = s['fixture']; w = f['warehouse_id']; base = f'/api/tradecase/warehouses/{w}'
    qa.step('expedition', 'PUT', base + '/stock/cells/' + f['receive'], dict(operation_id=qa.tag()+'.expedition', expected_version=1, zone_kind='EXPEDITION', reason='Owned original partial order proof'))
    if 'customer' not in s:
        s['customer'] = qa.expect(200, qa.http('POST', '/api/customers', dict(customer_code=qa.tag(), customer_name='Owned partial 80 BOX store', customer_type='LEGAL_ENTITY')))['customer_id']; qa.save()
    s.setdefault('day', (datetime.now(ZoneInfo('Europe/Moscow')).date()+timedelta(days=1)).isoformat()); qa.save()
    qa.send('recipient', 'RECIPIENT', 'C1', dict(title='Partial shipment allowed', wms_customer_id=s['customer'], target_owner_id='SNS', permitted_source_owners=['SNS'], buyout_mode='BEFORE_PICK', min_osg_days=0, lead_time_days=0, allow_broken_box=False, allow_partial_ship=True))
    qa.send('order', 'ORDER', 'O80', dict(recipient_id='C1', planned_ship_at=s['day']+'T12:00:00+03:00', lines=[dict(line_id='1', sku_id='A', source_owner_id='SNS', target_owner_id='SNS', mrc='200', quantity='800', uom='EA', min_osg_days=0)]))
    order = qa.native_order('native_order', 800)
    qa.step('binding', 'POST', base+'/orders/O80/binding', dict(operation_id=qa.tag()+'.binding', expected_order_version=1, customer_order_id=order['order'], lines=[dict(line_id='1', customer_order_row_id=order['row'])]))
    tasks = qa.wave('partial80', order['order']); assert len(tasks)==4 and all(t[4]==200 for t in tasks), tasks
    s['tasks'] = tasks; s['phase'] = 'WAVE'; qa.save(); assert qa.stock()[:2]==(800,800)


def pick():
    f=s['fixture']; w=f['warehouse_id']
    for i,(tid,pallet,src,dst,qty) in enumerate(s['tasks'],1):
        qa.step('move.'+str(tid),'POST',f'/api/warehouse-tasks/{tid}/complete',dict(operation_id=qa.tag()+'.move.'+str(tid),scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty)))
        if str(tid) not in s.setdefault('shipments',{}):
            s['shipments'][str(tid)]=dict(prepare_shipment(dict(fixture=f,native_order=s['native_order']['order'],shipment_identifier='P80.ST.'+str(tid),shipment_quantity=qty,st_number='P80.'+str(w)+'.'+str(i))),pallet=pallet,st_number='P80.'+str(w)+'.'+str(i),ordinal=i);qa.save()
        path=f'/api/warehouse-tasks/{tid}/full-pallet-shipment'
        if 'bind.'+str(tid) not in s.get('steps',{}):
            current=qa.expect(200,qa.http('GET',path))
            qa.step('bind.'+str(tid),'POST',path,dict(operation_id=qa.tag()+'.bind.'+str(tid),shipment_identifier=s['shipments'][str(tid)]['shipment_identifier'],scanned_pallet=pallet,expected_stock_version=current['stock_version']))
    s['picked']=qa.db('select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o group by STATUS',o=s['native_order']['order']);assert s['picked']==[('PICKED',4,800)],s['picked']
    s['phase']='PICKED';qa.save()


def transport():
    f=s['fixture'];w=f['warehouse_id'];first=next(iter(s['shipments'].values()))
    path=qa.OUT/'transport.json'
    if not path.exists():path.write_text(json.dumps(dict(warehouse_id=w,case_id=w,st_number=first['st_number'],vehicle_number='P80V'+str(w),dock='P80D'+str(w),shipment_date=s['day'],http=[])),encoding='utf-8')
    if 'transport' not in s:
        run=subprocess.run([sys.executable,'tests/tradecase/prepare_transport_task.py'],cwd=qa.ROOT,env=dict(os.environ,TRADECASE_TRANSPORT_FIXTURE=str(path)),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        assert run.returncode==0,(run.stdout+run.stderr)[-2000:]
        s['transport']={k:v for k,v in json.loads(path.read_text(encoding='utf-8')).items()if k!='http'};qa.save()
    t=s['transport']
    for key,ship in s['shipments'].items():qa.step('assign.'+key,'POST',f"/api/admin/transport/tasks/{t['transport_task_id']}/sts",dict(st_numbers=[ship['st_number']]))
    if 'profile' not in s.get('steps',{}):
        p=qa.expect(200,qa.http('GET',f"/api/admin/transport/vehicles/{t['vehicle_id']}/profile"))
        qa.step('profile','POST','/api/admin/transport/vehicle-profiles',dict(operation_id=qa.tag()+'.profile',vehicle_id=t['vehicle_id'],expected_source_hash=p['base_hash'],expected_version=p['version'],vehicle_size_class='QA_PARTIAL80',cargo_length_mm=3600,cargo_width_mm=800,cargo_height_mm=2600,outer_height_mm=3500,outer_length_mm=6000,floor_variants=[dict(code='QA3',limits=[dict(pallet_type_id=1,max_places=3)])],reason='Three owned pallet places for 60 BOX',evidence_reference='TEST_NOT_HARDWARE'))
    if 'next_trip' not in s:s['next_trip']=qa.step('next.trip','POST','/api/admin/transport/tasks',dict(transtype='10',shipment_date=s['day']))['task_id'];qa.save()
    s['phase']='TRANSPORT';qa.save()


def load():
    f=s['fixture']; t=s['transport']
    for key,ship in s['shipments'].items():
        if 'floor.'+key not in s['steps']:
            p=qa.expect(200,qa.http('GET','/api/inventory/pallet-floor-types?identifier='+ship['pallet']))
            qa.step('floor.'+key,'POST','/api/inventory/pallet-floor-types',dict(operation_id=qa.tag()+'.floor.'+key,identifier=ship['pallet'],pallet_type_id=1,expected_version=p['version'],scan_pallet=ship['pallet'],scan_cell=p['cell'],evidence_reference='OWN_SYNTHETIC_PALLET_NOT_HARDWARE'))
        ident=ship['shipment_identifier']; path='/api/outgoing-quality/'+ident
        n=next(k for k,p in s['pallets'].items()if p['pallet']==ship['pallet'])
        if 'qc.'+key not in s['steps']:
            qc=qa.expect(200,qa.http('GET',path))
            scans=[dict(system_code='CRPT',profile_code='TOBACCO',code=f['gtin']+f['tag'][:2]+n+str(i).zfill(3))for i in range(1,201)]
            qa.step('qc.'+key,'POST',path+'/scan',dict(operation_id=qa.tag()+'.qc.'+key,expected_composition_signature=qc['composition_signature'],error_count=0,scans=scans))
        if 'load.'+key not in s['steps']:
            p=qa.expect(200,qa.http('GET','/api/transport/loading/single-preview?shipment_identifier='+ident))
            body=dict(operation_id=qa.tag()+'.load.'+key,identifier=ident,expected_version=p['expected_version'],expected_composition_signature=p['composition_signature'],scan_container=ship['pallet'],scan_cell=p['snapshot']['cell'],transport_task_id=t['transport_task_id'],scan_vehicle=t['vehicle_number'],scan_dock=t['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=p['expected_version'],gross_weight_kg='200',width_m='1.2',depth_m='0.8',height_m='2.5'))
            answer=qa.step('load.'+key,'POST','/api/transport/loading/confirm-single',body,status=409 if ship['ordinal']==4 else 200)
            if ship['ordinal']!=4:assert qa.expect(200,qa.http('POST','/api/transport/loading/confirm-single',body))==answer
        if ship['ordinal']==4:
            answer=s['steps']['load.'+key]['result']
            assert answer['detail']['code']=='STOCK_RULE_REJECTED' and answer['detail']['message']=='LOAD_FLOOR_PHYSICAL_VARIANT_NOT_CONFIRMED',answer
    s['after_load']=qa.stock();assert s['after_load']==(200,200,1),s['after_load']
    s['phase']='PARTIAL_LOADED';qa.save()


def defer():
    ship=next(x for x in s['shipments'].values()if x['ordinal']==4); path='/api/transport/st-deferrals'
    if 'defer' not in s['steps']:
        c=qa.expect(200,qa.http('GET',path+'/context?st_number='+ship['st_number']));s['before_deferral']=c;qa.save()
        assert c['physical_preparation']['state']=='PREPARED_WHOLE_STOCK',c
        body=dict(operation_id=qa.tag()+'.defer',st_number=ship['st_number'],target_trip_id=s['next_trip'],expected_version=c['version'],source_hash=c['source_hash'],reason='Keep unshipped 20 BOX of the same 80 BOX order for next trip',reference='PROGRAM_SECTION8_80_60_20_SYNTHETIC')
        answer=qa.step('defer','POST',path,body)
        assert qa.expect(200,qa.http('POST',path,body))==answer
    s['retained']=qa.expect(200,qa.http('GET',path+'/context?st_number='+ship['st_number']))
    assert s['retained']['source_trip_id']==s['next_trip']
    assert qa.stock()==(200,200,1)
    s['phase']='DEFERRED';qa.save()


def documents():
    w=s['fixture']['warehouse_id'];t=s['transport'];base=f'/api/tradecase/warehouses/{w}'
    payload=dict(vehicle_id=t['vehicle_number'],planning_source='SAP',planned_departure_at=s['day']+'T12:00:00+03:00',capacity_kg='1000',capacity_m3='7.488',orders=[dict(order_id='O80',line_id='1',quantity='600')])
    qa.send('trip_partial','TRIP','T60',payload)
    composition=qa.step('composition','POST','/api/tradecase/order-compositions/report',dict(warehouse_id=w,order_id='O80'))
    assert composition['units']==composition['codes']==800,composition
    for system,sender in [('SAP','TC03.SAP'),('SKM','TC03.SKM')]:
        qa.step('composition.'+system,'POST','/api/tradecase/order-compositions/acknowledgments',dict(schema_version=1,warehouse_id=w,order_id='O80',system_code=system,sender_id=sender,event_id=qa.tag()+'.composition.'+system,composition_no=composition['composition_no'],signature=composition['signature'],outcome='ACCEPTED',occurred_at=datetime.now(timezone.utc).isoformat()))
    route=base+'/trips/T60'
    qa.step('trip.binding','POST',route+'/binding',dict(operation_id=qa.tag()+'.trip.bind',native_task_id=t['transport_task_id'],expected_trip_version=1,expected_binding_version=0))
    if 'trip.document' not in s['steps']:
        execution=qa.expect(200,qa.http('GET',route+'/execution'))
        qa.step('trip.document','POST',route+'/transport-document',dict(operation_id=qa.tag()+'.trip.doc',source_id='TC03.SAP',external_event_id=qa.tag()+'.trip.doc',expected_trip_version=1,expected_binding_version=1,document_version=1,document_status='READY',external_document_id='TEST_PARTIAL_NOT_INDUSTRIAL',manifest_signature=execution['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat()))
    s['phase']='DOCUMENT_READY';qa.save()


def depart():
    t=s['transport'];path=f"/api/transport/loading/{t['transport_task_id']}/depart"
    body=dict(operation_id=qa.tag()+'.depart');answer=qa.step('depart','POST',path,body)
    assert qa.expect(200,qa.http('POST',path,body))==answer
    assert qa.stock()==(200,200,1)
    s['partial_fulfillment']=qa.db('select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o group by STATUS order by STATUS',o=s['native_order']['order'])
    assert s['partial_fulfillment']==[('PICKED',1,200),('SHIPPED',3,600)],s['partial_fulfillment']
    s['retained_codes']=qa.db('select u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID,a.OWNER_ID,r.CELL from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY join RRL_REMAINS r on r.UID_POLETA=u.UID_PALLET and r.REMAIN>0 join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and u.STOCK_STATUS=\'AVAILABLE\' order by u.PHYSICAL_UNIT_KEY',w=s['fixture']['warehouse_id'])
    assert len(s['retained_codes'])==200 and all(x[1] and x[2]=='SNS' and x[3] for x in s['retained_codes'])
    s['phase']='PARTIAL_DEPARTED';s['quantity_boxes']=dict(ordered=80,picked=80,shipped=60,retained=20);qa.save()


def strict_policy():
    profile=dict(s['steps']['msg_recipient']['body']['payload']);profile.pop('entity_type');profile['allow_partial_ship']=False
    qa.send('strict.recipient','RECIPIENT','STRICT',profile)
    order=dict(s['steps']['msg_order']['body']['payload']);order.pop('entity_type');order['recipient_id']='STRICT'
    qa.send('strict.order','ORDER','STRICT80',order)
    trip=dict(s['steps']['msg_trip_partial']['body']['payload']);trip.pop('entity_type');trip['orders']=[dict(order_id='STRICT80',line_id='1',quantity='600')]
    body=dict(schema_version=1,event_id=qa.tag()+'.strict.trip',source_id='TC03.SAP',warehouse_id=s['fixture']['warehouse_id'],document_id='STRICT60',version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type='TRIP',**trip))
    result=qa.step('strict.rejected','POST','/api/tradecase/messages',body,status=409)
    assert result['detail']['code']=='PARTIAL_SHIPMENT_NOT_ALLOWED',result
    assert qa.expect(409,qa.http('POST','/api/tradecase/messages',body))==result
    qa.send('strict.cancel','ORDER','STRICT80',dict(order,cancelled=True),version=2)
    assert qa.stock()==(200,200,1)
    s['strict_policy']='PASS';qa.save()


def continue_transport():
    assert s['phase']=='PARTIAL_DEPARTED'
    f=s['fixture'];w=f['warehouse_id'];ship=next(x for x in s['shipments'].values()if x['ordinal']==4)
    path=qa.OUT/'remaining-transport.json'
    if not path.exists():path.write_text(json.dumps(dict(warehouse_id=w,case_id=w,st_number=ship['st_number'],vehicle_number='P80RV'+str(w),dock=s['transport']['dock'],shipment_date=s['day'],transport_task_id=s['next_trip'],http=[])),encoding='utf-8')
    if 'remaining_transport'not in s:
        run=subprocess.run([sys.executable,'tests/tradecase/prepare_transport_task.py'],cwd=qa.ROOT,env=dict(os.environ,TRADECASE_TRANSPORT_FIXTURE=str(path)),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        assert run.returncode==0,(run.stdout+run.stderr)[-2000:]
        s['remaining_transport']={k:v for k,v in json.loads(path.read_text(encoding='utf-8')).items()if k!='http'};qa.save()
    t=s['remaining_transport']
    if 'remaining.profile'not in s['steps']:
        p=qa.expect(200,qa.http('GET',f"/api/admin/transport/vehicles/{t['vehicle_id']}/profile"))
        qa.step('remaining.profile','POST','/api/admin/transport/vehicle-profiles',dict(operation_id=qa.tag()+'.remaining.profile',vehicle_id=t['vehicle_id'],expected_source_hash=p['base_hash'],expected_version=p['version'],vehicle_size_class='QA_RETAINED20',cargo_length_mm=1200,cargo_width_mm=800,cargo_height_mm=2600,outer_height_mm=3500,outer_length_mm=6000,floor_variants=[dict(code='QA1',limits=[dict(pallet_type_id=1,max_places=1)])],reason='Dispatch the previously retained owned 20 BOX separately',evidence_reference='TEST_NOT_HARDWARE'))
    s['phase']='REMAINDER_TRANSPORT';qa.save()


def continue_load():
    ship=next(x for x in s['shipments'].values()if x['ordinal']==4);t=s['remaining_transport'];f=s['fixture']
    path='/api/outgoing-quality/'+ship['shipment_identifier']
    if 'remaining.qc'not in s['steps']:
        qc=qa.expect(200,qa.http('GET',path));n=next(k for k,v in s['pallets'].items()if v['pallet']==ship['pallet'])
        scans=[dict(system_code='CRPT',profile_code='TOBACCO',code=f['gtin']+f['tag'][:2]+n+str(i).zfill(3))for i in range(1,201)]
        qa.step('remaining.qc','POST',path+'/scan',dict(operation_id=qa.tag()+'.remaining.qc',expected_composition_signature=qc['composition_signature'],error_count=0,scans=scans))
    if 'remaining.load'not in s['steps']:
        p=qa.expect(200,qa.http('GET','/api/transport/loading/single-preview?shipment_identifier='+ship['shipment_identifier']))
        body=dict(operation_id=qa.tag()+'.remaining.load',identifier=ship['shipment_identifier'],expected_version=p['expected_version'],expected_composition_signature=p['composition_signature'],scan_container=ship['pallet'],scan_cell=p['snapshot']['cell'],transport_task_id=t['transport_task_id'],scan_vehicle=t['vehicle_number'],scan_dock=t['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=p['expected_version'],gross_weight_kg='200',width_m='1.2',depth_m='0.8',height_m='2.5'))
        result=qa.step('remaining.load','POST','/api/transport/loading/confirm-single',body)
        assert qa.expect(200,qa.http('POST','/api/transport/loading/confirm-single',body))==result
    assert qa.stock()[:2]==(0,0)
    s['phase']='REMAINDER_LOADED';qa.save()


def continue_depart():
    w=s['fixture']['warehouse_id'];t=s['remaining_transport'];base=f'/api/tradecase/warehouses/{w}'
    payload=dict(vehicle_id=t['vehicle_number'],planning_source='SAP',planned_departure_at=s['day']+'T16:00:00+03:00',capacity_kg='1000',capacity_m3='2.496',orders=[dict(order_id='O80',line_id='1',quantity='200')])
    qa.send('remaining.trip','TRIP','T20',payload)
    composition=qa.step('remaining.composition','POST','/api/tradecase/order-compositions/report',dict(warehouse_id=w,order_id='O80'));assert composition['units']==800
    for system,sender in [('SAP','TC03.SAP'),('SKM','TC03.SKM')]:
        qa.step('remaining.composition.'+system,'POST','/api/tradecase/order-compositions/acknowledgments',dict(schema_version=1,warehouse_id=w,order_id='O80',system_code=system,sender_id=sender,event_id=qa.tag()+'.remaining.composition.'+system,composition_no=composition['composition_no'],signature=composition['signature'],outcome='ACCEPTED',occurred_at=datetime.now(timezone.utc).isoformat()))
    path=base+'/trips/T20'
    qa.step('remaining.binding','POST',path+'/binding',dict(operation_id=qa.tag()+'.remaining.binding',native_task_id=t['transport_task_id'],expected_trip_version=1,expected_binding_version=0))
    if 'remaining.document'not in s['steps']:
        state=qa.expect(200,qa.http('GET',path+'/execution'))
        qa.step('remaining.document','POST',path+'/transport-document',dict(operation_id=qa.tag()+'.remaining.doc',source_id='TC03.SAP',external_event_id=qa.tag()+'.remaining.doc',expected_trip_version=1,expected_binding_version=1,document_version=1,document_status='READY',external_document_id='TEST_RETAINED20_NOT_INDUSTRIAL',manifest_signature=state['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat()))
    path=f"/api/transport/loading/{t['transport_task_id']}/depart";body=dict(operation_id=qa.tag()+'.remaining.depart');answer=qa.step('remaining.depart','POST',path,body)
    assert qa.expect(200,qa.http('POST',path,body))==answer
    s['phase']='ALL_DEPARTED';qa.save()


def finish():
    assert s['phase']=='ALL_DEPARTED'
    wave=s['partial80_wave_id'];path=f'/api/picking/waves/{wave}'
    execution=qa.expect(200,qa.http('GET',path+'/execution'));assert execution['ready'],execution
    qa.step('finish','POST',path+'/finish-execution',dict(operation_id=qa.tag()+'.finish'))
    assert qa.db('select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o group by STATUS',o=s['native_order']['order'])==[('SHIPPED',4,800)]
    assert qa.stock()==(0,0,0)
    assert qa.db("select count(*)from USER_OBJECTS where STATUS='INVALID'")==[(0,)]
    s['final_order']=qa.expect(200,qa.http('GET',f"/api/tradecase/warehouses/{s['fixture']['warehouse_id']}/documents/ORDER/O80"))
    assert s['final_order']['execution']['items'][0]['boxes']==dict(ordered='80',picked='80',loaded='80',shipped='80',retained='0')
    s['phase']='CLOSED';s['status']='PASS';qa.save()


def main():
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[\x60,)\s]',(qa.ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    assert s.get('phase')!='CLOSED','Never reopen a closed proof'
    stage=sys.argv[1]
    if stage=='receive':
        qa.main();return
    try:
        globals()[stage]();print(json.dumps(dict(phase=s['phase'],stock=qa.stock())))
    except Exception as exc:
        s['error']=str(exc)[:3000];qa.save();raise
    finally:
        s.setdefault('http',[]).extend(qa.CALLS);qa.save()


if __name__=='__main__':main()
