"""660 independent 10-EA inventory places, native whole-unit pick/load/depart.

This scale fixture has one SKU/order/recipient, not the original three-order/1100-BOX program.
External replies, dimensions and weights are synthetic. No physical stock is inserted with SQL.
"""
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).parent))
import live_topup_physical_660 as q
from full_pallet_fixture import prepare_shipment

q.OUT=q.ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/physical'
q.STATE=q.OUT/'state.json'
q.PALLETS=q.MAIN_PALLETS=660
q.UNITS=10
if q.STATE.exists():q.s.update(json.loads(q.STATE.read_text(encoding='utf-8')))
s=q.s
original_step=q.step


def bounded_step(key,method,path,body=None,status=200):
    if 'result'not in s.get('steps',{}).get(key,{}) and datetime.now(ZoneInfo('Europe/Moscow'))>=datetime(2026,10,26,23,55,tzinfo=ZoneInfo('Europe/Moscow')):
        raise RuntimeError('Stop new fixture commands at 23:55; preserve state before midnight')
    return original_step(key,method,path,body,status)


q.step=bounded_step


def setup():
    if 'fixture' in s:return
    if 'planned' not in s:
        uid,ware=q.plan_fixture();s['planned']=dict(uid=uid,warehouse=ware);q.save()
    original=q.live_stock_acceptance.uuid4
    q.live_stock_acceptance.uuid4=lambda:type('Tag',(),dict(hex=s['planned']['uid']))()
    try:f=q.setup()
    finally:q.live_stock_acceptance.uuid4=original
    assert f['warehouse_id']==s['planned']['warehouse']
    s['fixture']={k:v for k,v in f.items()if k!='password'};q.save()
    with q.oracle_connection()as c:
        cur=c.cursor();cur.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
        try:
            cur.execute('update RRL_ARTICULS set COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=10,DIMKOR_X=0.4,DIMKOR_Y=0.5,DIMKOR_Z=0.5,NORMA_UKLADKI=1,COUNT_IN_ROW=1,ROWS_IN_PAL=1 where ACTICUL=:a',a=f['article']);assert cur.rowcount==1;c.commit()
        finally:cur.callproc('RRL_STOCK_CONFIG_API.end_change')
    s['phase']='SETUP';q.save()


def prepare():
    f=s['fixture'];w=f['warehouse_id'];base=f'/api/tradecase/warehouses/{w}'
    q.step('expedition','PUT',base+'/stock/cells/'+f['receive'],dict(operation_id=q.tag()+'.expedition',expected_version=1,zone_kind='EXPEDITION',reason='Owned independent-place scale fixture'))
    if 'customer'not in s:
        s['customer']=q.expect(200,q.http('POST','/api/customers',dict(customer_code=q.tag(),customer_name='660-place scale fixture',customer_type='LEGAL_ENTITY')))['customer_id'];q.save()
    s.setdefault('day',(datetime.now(ZoneInfo('Europe/Moscow')).date()+timedelta(days=1)).isoformat());q.save()
    q.send('recipient','RECIPIENT','C1',dict(title='Owned scale recipient',wms_customer_id=s['customer'],target_owner_id='SNS',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',min_osg_days=0,lead_time_days=0,allow_broken_box=False,allow_partial_ship=True))
    q.send('order','ORDER','O660',dict(recipient_id='C1',planned_ship_at=s['day']+'T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='SNS',mrc='200',quantity='6600',uom='EA',min_osg_days=0)]))
    order=q.native_order('native_order',6600)
    q.step('binding','POST',base+'/orders/O660/binding',dict(operation_id=q.tag()+'.binding',expected_order_version=1,customer_order_id=order['order'],lines=[dict(line_id='1',customer_order_row_id=order['row'])]))
    s['tasks']=q.wave(s.get('wave_key','scale660'),order['order']);q.save()
    assert len(s['tasks'])==660 and all(t[4]==10 for t in s['tasks']),[(t[0],t[4])for t in s['tasks']]
    s['phase']='WAVE';q.save()


def prepare_after_source_bound():
    assert 'PICK_PLAN_SOURCE_STOCK_BOUND_500' in s.get('error','')
    assert q.stock()==(6600,0,660)
    s['wave_key']='scale660_sources1000';q.save()
    prepare()


def launch_after_wave_bound():
    assert 'WAVE_LAUNCH_BATCH_BOUND' in s.get('error','') or ('REQUEST_DEADLINE' in s.get('error','') and 'launch_places1000' in s['steps'])
    key=s['wave_key'];wave=s['steps'][key+'_wave']['result']['pick_wave_id'];route=f'/api/picking/waves/{wave}'
    q.step('launch_places1000','POST',route+'/launch',dict(operation_id=q.tag()+'.launch.places1000'))
    q.step('staging_places1000','POST',route+'/staging/release',dict(to_cell=s['fixture']['receive']))
    q.step('release_places1000','POST',route+'/release-picking',dict(operation_id=q.tag()+'.release.places1000'))
    s[key+'_wave_id']=wave
    s['tasks']=q.db("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='PICKING_MOVE'order by TASK_ID",w=wave)
    assert len(s['tasks'])==660 and all(t[4]==10 for t in s['tasks'])
    assert q.stock()==(6600,6600,660)
    s['phase']='WAVE';q.save()


def pick():
    f=s['fixture'];w=f['warehouse_id']
    for i,(tid,pallet,src,dst,qty) in enumerate(s['tasks'],1):
        q.step('move.'+str(tid),'POST',f'/api/warehouse-tasks/{tid}/complete',dict(operation_id=q.tag()+'.move.'+str(tid),scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty)))
        if str(tid) not in s.setdefault('shipments',{}):
            st='CT.'+str(w)+'.'+str(i)
            s['shipments'][str(tid)]=dict(prepare_shipment(dict(fixture=f,native_order=s['native_order']['order'],shipment_identifier='CT.ST.'+str(tid),shipment_quantity=qty,st_number=st)),pallet=pallet,st_number=st,ordinal=i);q.save()
        path=f'/api/warehouse-tasks/{tid}/full-pallet-shipment'
        if 'bind.'+str(tid)not in s['steps']:
            current=q.expect(200,q.http('GET',path))
            q.step('bind.'+str(tid),'POST',path,dict(operation_id=q.tag()+'.bind.'+str(tid),shipment_identifier=s['shipments'][str(tid)]['shipment_identifier'],scanned_pallet=pallet,expected_stock_version=current['stock_version']))
        if i%25==0:print('Picked places',i,'of 660',flush=True)
    assert q.stock()==(6600,6600,660)
    s['phase']='PICKED';q.save()


def transport():
    f=s['fixture'];w=f['warehouse_id'];first=next(iter(s['shipments'].values()));file=q.OUT/'transport.json'
    if not file.exists():file.write_text(json.dumps(dict(warehouse_id=w,case_id=w,st_number=first['st_number'],vehicle_number='CT26V'+str(w),dock='CT26D'+str(w),shipment_date=s['day'],http=[])),encoding='utf-8')
    if 'transport'not in s:
        result=subprocess.run([sys.executable,'tests/tradecase/prepare_transport_task.py'],cwd=q.ROOT,env=dict(os.environ,TRADECASE_TRANSPORT_FIXTURE=str(file)),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        assert result.returncode==0,(result.stdout+result.stderr)[-2000:]
        s['transport']={k:v for k,v in json.loads(file.read_text(encoding='utf-8')).items()if k!='http'};q.save()
    t=s['transport']
    if 'box_type'not in s:
        s['box_type']=q.step('box.type','POST','/api/case-pick/pallet-types',dict(pallet_type_code='CT26_'+f['tag'],pallet_type_name='Owned independent carton scale type',load_unit_class='BOX',default_volume_m3='0.1',default_weight_kg='0',length_mm=500,width_mm=400,height_mm=500))['pallet_type_id'];q.save()
    # Keep native physical capacity and its configuration hash consistent before the profile is saved.
    q.step('vehicle.capacity','PATCH',f"/api/admin/transport/vehicles/{t['vehicle_id']}",dict(num_plat=t['vehicle_number'],transtype_id='10',max_weight_kg=8000,max_pallets=660,sobstvennyy=True))
    if 'profile'not in s['steps']:
        p=q.expect(200,q.http('GET',f"/api/admin/transport/vehicles/{t['vehicle_id']}/profile"))
        q.step('profile','POST','/api/admin/transport/vehicle-profiles',dict(operation_id=q.tag()+'.profile',vehicle_id=t['vehicle_id'],expected_source_hash=p['base_hash'],expected_version=p['version'],vehicle_size_class='QA_CARTON',cargo_length_mm=13200,cargo_width_mm=2500,cargo_height_mm=2000,outer_height_mm=3000,outer_length_mm=14000,floor_variants=[dict(code='C660',limits=[dict(pallet_type_id=s['box_type'],max_places=660)])],reason='660 independent measured places, not pallet-mode source acceptance',evidence_reference='TEST_NOT_HARDWARE'))
    shipments=list(s['shipments'].values())
    for i in range(0,len(shipments),100):
        q.step('assign.'+str(i),'POST',f"/api/admin/transport/tasks/{t['transport_task_id']}/sts",dict(st_numbers=[x['st_number']for x in shipments[i:i+100]]))
    s['phase']='TRANSPORT';q.save()


def load():
    t=s['transport'];f=s['fixture']
    for i,(key,ship)in enumerate(s['shipments'].items(),1):
        if 'floor.'+key not in s['steps']:
            p=q.expect(200,q.http('GET','/api/inventory/pallet-floor-types?identifier='+ship['pallet']))
            q.step('floor.'+key,'POST','/api/inventory/pallet-floor-types',dict(operation_id=q.tag()+'.floor.'+key,identifier=ship['pallet'],pallet_type_id=s['box_type'],expected_version=p['version'],scan_pallet=ship['pallet'],scan_cell=p['cell'],evidence_reference='OWN_SYNTHETIC_CARTON'))
        if 'qc.'+key not in s['steps']:
            path='/api/outgoing-quality/'+ship['shipment_identifier'];p=q.expect(200,q.http('GET',path))
            codes=q.db('select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where u.CURRENT_UID=:p',p=ship['pallet']);assert len(codes)==10
            q.step('qc.'+key,'POST',path+'/scan',dict(operation_id=q.tag()+'.qc.'+key,expected_composition_signature=p['composition_signature'],error_count=0,scans=[dict(system_code=system,profile_code='TOBACCO',code=code)for system,code in codes]))
        if 'load.'+key not in s['steps']:
            p=q.expect(200,q.http('GET','/api/transport/loading/single-preview?shipment_identifier='+ship['shipment_identifier']))
            q.step('load.'+key,'POST','/api/transport/loading/confirm-single',dict(operation_id=q.tag()+'.load.'+key,identifier=ship['shipment_identifier'],expected_version=p['expected_version'],expected_composition_signature=p['composition_signature'],scan_container=ship['pallet'],scan_cell=p['snapshot']['cell'],transport_task_id=t['transport_task_id'],scan_vehicle=t['vehicle_number'],scan_dock=t['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=p['expected_version'],gross_weight_kg='10',width_m='0.4',depth_m='0.5',height_m='0.5')))
        if i%25==0:print('Loaded places',i,'of 660',flush=True)
    assert q.stock()==(0,0,0)
    s['phase']='LOADED';q.save()


def documents():
    w=s['fixture']['warehouse_id'];t=s['transport'];base=f'/api/tradecase/warehouses/{w}'
    payload=dict(vehicle_id=t['vehicle_number'],planning_source='SAP',planned_departure_at=s['day']+'T12:00:00+03:00',capacity_kg='8000',capacity_m3='66',orders=[dict(order_id='O660',line_id='1',quantity='6600')])
    q.send('trip','TRIP','T660',payload)
    composition=q.step('composition','POST','/api/tradecase/order-compositions/report',dict(warehouse_id=w,order_id='O660'))
    assert composition['units']==composition['codes']==6600,composition
    for system,sender in [('SAP','TC03.SAP'),('SKM','TC03.SKM')]:
        q.step('composition.'+system,'POST','/api/tradecase/order-compositions/acknowledgments',dict(schema_version=1,warehouse_id=w,order_id='O660',system_code=system,sender_id=sender,event_id=q.tag()+'.composition.'+system,composition_no=composition['composition_no'],signature=composition['signature'],outcome='ACCEPTED',occurred_at=datetime.now(timezone.utc).isoformat()))
    route=base+'/trips/T660'
    q.step('trip.binding','POST',route+'/binding',dict(operation_id=q.tag()+'.trip.bind',native_task_id=t['transport_task_id'],expected_trip_version=1,expected_binding_version=0))
    if 'trip.document'not in s['steps']:
        execution=q.expect(200,q.http('GET',route+'/execution'));s['execution_before_depart']=execution;q.save()
        assert len(execution['loads'])==660,execution.keys()
        q.step('trip.document','POST',route+'/transport-document',dict(operation_id=q.tag()+'.trip.doc',source_id='TC03.SAP',external_event_id=q.tag()+'.trip.doc',expected_trip_version=1,expected_binding_version=1,document_version=1,document_status='READY',external_document_id='TEST_SCALE_NOT_INDUSTRIAL',manifest_signature=execution['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat()))
    s['phase']='DOCUMENT_READY';q.save()


def depart():
    t=s['transport'];path=f"/api/transport/loading/{t['transport_task_id']}/depart"
    body=dict(operation_id=q.tag()+'.depart')
    result=q.step('depart','POST',path,body)
    assert q.expect(200,q.http('POST',path,body))==result
    assert result['physical_places']==660 and q.stock()==(0,0,0),result
    s['phase']='DEPARTED';q.save()


def finish():
    assert s['phase']=='DEPARTED'
    f=s['fixture'];w=f['warehouse_id']
    s['final_fulfillment']=q.db('select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o group by STATUS',o=s['native_order']['order'])
    assert s['final_fulfillment']==[('SHIPPED',660,6600)],s['final_fulfillment']
    assert q.stock()==(0,0,0)
    wave=s[s.get('wave_key','scale660')+'_wave_id']
    q.expect(200,q.http('POST',f'/api/picking/waves/{wave}/refresh-sync',{}))
    assert q.db('select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:w',w=wave)==[('DONE',)]
    with q.oracle_connection()as c:
        cur=c.cursor()
        cur.execute("update RUSERS set DELETED=1 where ID=:u and WARE_ID=:w and USER_GROUP='TC03QA'",u=f['actor'],w=w)
        cur.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where USERNAME=:u and REVOKED_AT is null',u=f['actor']);c.commit()
        cur.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert cur.fetchone()[0]==0
    s['phase']='CLOSED';s['status']='PASS_SCALE_ONLY';q.save()


def main():
    os.environ['TRADECASE_ADMIN_USER']='admin'
    os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(q.ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    assert s.get('phase')!='CLOSED','Never reopen a closed fixture'
    try:
        setup()
        stage=sys.argv[1]if len(sys.argv)>1 else 'receive'
        q.receive()if stage=='receive'else globals()[stage]()
        print(json.dumps(dict(phase=s.get('phase'),warehouse=s['fixture']['warehouse_id'])))
    except Exception as error:s['error']=str(error);q.save();raise
    finally:s.setdefault('http',[]).extend(q.CALLS);q.save()


if __name__=='__main__':main()
