"""Isolated native vehicle-change acceptance; reuse owned nested-shipment writers."""
import json
import sys
from uuid import uuid4
import live_nested_shipping as nested

OUT=nested.qa.ROOT/'runtime/test-evidence/tradecase/2026-10-23/T07/vehicle-change'
FILE=OUT/'vehicle-change.json'
OUT.mkdir(parents=True,exist_ok=True)
s=json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else dict(tag='VC23.'+uuid4().hex[:9],requests={},results={})
nested.OUT=OUT;nested.FILE=FILE;nested.s=s
qa=nested.qa
sys.path.insert(0,str(qa.ROOT/'api/wms_api_server'))
qa.OUT=OUT;qa.FILE=FILE;qa.s=s
s['previous_calls']=s.get('calls',[])

def vehicles():
    t=s['transport']
    s.setdefault('vehicles',{'A':dict(id=t['vehicle_id'],number=t['vehicle_number'])})
    for name in ['B','C']:
        if name not in s['vehicles']:
            number='VC23'+name+str(s['warehouse'])
            result=qa.step('create_vehicle_'+name,'/api/admin/transport/vehicles',dict(num_plat=number,transtype_id='10',max_weight_kg=1000,max_pallets=10,sobstvennyy=True),status=201)
            s['vehicles'][name]=dict(id=result['id'],number=number);qa.save()
        vehicle=s['vehicles'][name]
        profile=qa.expect(200,qa.http('GET',f"/api/admin/transport/vehicles/{vehicle['id']}/profile"))
        qa.step('profile_'+name,'/api/admin/transport/vehicle-profiles',dict(operation_id=s['tag']+'.profile.'+name,vehicle_id=vehicle['id'],expected_source_hash=profile['base_hash'],expected_version=profile['version'],vehicle_size_class='QA_VAN',cargo_length_mm=3000,cargo_width_mm=2400,cargo_height_mm=2400,outer_height_mm=3000,outer_length_mm=6000,floor_variants=[dict(code='QA_TWO_EURO',limits=[dict(pallet_type_id=1,max_places=2)])],reason='Owned vehicle replacement synthetic geometry',evidence_reference='SYNTHETIC_NOT_ROAD_VEHICLE'))
    s['status']='VEHICLES_READY_UI_A_TO_B_PENDING';s.pop('error',None);qa.save()


def accept_ui_and_load():
    ui=json.loads((OUT/'vehicle-live-ui.json').read_text(encoding='utf-8'))
    assert ui['status']=='PASS' and len(ui['posts'])==1
    trip=s['transport']['transport_task_id']
    current=qa.expect(200,qa.http('GET',f'/api/admin/transport/tasks/{trip}'))
    assert current['TRANSPORT']==s['vehicles']['B']['number']
    assert qa.query('select count(*)from RRL_SBORKA_PALLETS where TRANSTASK_ID=:t and ID=:p',t=trip,p=s['transport']['case_id'])==[(1,)]
    path=OUT/'transport.json';transport=json.loads(path.read_text(encoding='utf-8'))
    transport.update(vehicle_id=s['vehicles']['B']['id'],vehicle_number=s['vehicles']['B']['number'])
    path.write_text(json.dumps(transport,indent=2),encoding='utf-8');s['transport']=transport
    original=qa.step
    def checked(key,path,body=None,**kwargs):
        if key=='load_with_tare' and 'old_vehicle_denied' not in s['results']:
            original('old_vehicle_denied',path,dict(body,operation_id=s['tag']+'.wrong_A',scan_vehicle=s['vehicles']['A']['number']),status=409)
        return original(key,path,body,**kwargs)
    qa.step=checked
    try:nested.load()
    finally:qa.step=original
    qa.step('loaded_blocks_C',f'/api/admin/transport/tasks/{trip}',dict(transport=s['vehicles']['C']['number']),method='PATCH',status=409)
    assert qa.expect(200,qa.http('GET',f'/api/admin/transport/tasks/{trip}'))['TRANSPORT']==s['vehicles']['B']['number']
    s['status']='LOADED_B_REASSIGN_DENIED';qa.save()


def trade_base():
    return f"/api/tradecase/warehouses/{s['warehouse']}/trips/R1.{s['transport']['case_id']}"


def trip_document(vehicle,version):
    from datetime import datetime,timezone
    tr=s['transport'];tag=s['tag'];base=trade_base()
    message=dict(schema_version=1,event_id=tag+'.trip.'+str(version),source_id='TC03.SAP',warehouse_id=s['warehouse'],document_id='R1.'+str(tr['case_id']),version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(entity_type='TRIP',vehicle_id=vehicle['number'],planning_source='SAP',planned_departure_at=tr['planned_departure_at'],capacity_kg='1000',capacity_m3='17.28',orders=[dict(order_id=tr['demand_order_id'],line_id='1',quantity='10')]))
    qa.step('external_trip_'+str(version),'/api/tradecase/messages',message)
    qa.step('binding_'+str(version),base+'/binding',dict(operation_id=tag+'.bind.'+str(version),native_task_id=tr['transport_task_id'],expected_trip_version=version,expected_binding_version=version-1))
    state=qa.expect(200,qa.http('GET',base+'/execution'))
    if version==2:
        assert not state['document_ready'],state
        blocked=qa.step('new_binding_old_document_denied',f"/api/transport/loading/{tr['transport_task_id']}/depart",dict(operation_id=tag+'.stale_doc.depart'),status=409)
        assert 'DOCUMENT' in json.dumps(blocked),blocked
    body=dict(operation_id=tag+'.doc.'+str(version),source_id='TC03.SAP',external_event_id=tag+'.doc.'+str(version),expected_trip_version=version,expected_binding_version=version,document_version=version,document_status='READY',external_document_id='TEST_VEHICLE_DOC_'+str(version),manifest_signature=state['manifest_signature'],occurred_at=datetime.now(timezone.utc).isoformat())
    qa.step('ready_'+str(version),base+'/transport-document',body)
    after=qa.expect(200,qa.http('GET',base+'/execution'));assert after['document_ready'],after
    s['document_state_'+str(version)]=after;qa.save()


def unload_change():
    tr=s['transport'];trip=tr['transport_task_id']
    trip_document(s['vehicles']['B'],1)
    load=s['requests']['load_with_tare']['body']
    body=dict(operation_id=s['tag']+'.unload.B',load_operation_id=load['operation_id'],expected_version=load['expected_version'],scan_container=load['scan_container'],scan_cell=load['scan_cell'],scan_vehicle=load['scan_vehicle'],scan_dock=load['scan_dock'],reason='Owned physical removal before vehicle replacement')
    value=qa.step('unload_B','/api/transport/loading/unload',body)
    assert qa.expect(200,qa.http('POST','/api/transport/loading/unload',body))==value
    assert qa.query('select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse'])==[(10,10)]
    # Old exact load reply does not reload the pallet.
    assert qa.expect(200,qa.http('POST','/api/transport/loading/confirm',load))==s['results']['load_with_tare']
    qa.step('change_C',f'/api/admin/transport/tasks/{trip}',dict(transport=s['vehicles']['C']['number']),method='PATCH')
    current=qa.expect(200,qa.http('GET',f'/api/admin/transport/tasks/{trip}'));assert current['TRANSPORT']==s['vehicles']['C']['number']
    tr.update(vehicle_id=s['vehicles']['C']['id'],vehicle_number=s['vehicles']['C']['number'])
    (OUT/'transport.json').write_text(json.dumps(tr,indent=2),encoding='utf-8')
    state=qa.expect(200,qa.http('GET',trade_base()+'/execution'));s['old_document_after_change']=state
    assert not state['document_ready'],state
    s['status']='UNLOADED_CHANGED_C';qa.save()


def reload_c():
    tr=s['transport'];root=nested.snapshot(s['root']);v=root['nodes'][0]['version']
    body=dict(s['requests']['load_with_tare']['body'],operation_id=s['tag']+'.reload.C',expected_version=v,scan_vehicle=tr['vehicle_number'],measurements=dict(s['requests']['load_with_tare']['body']['measurements'],content_version=v),physical_boxes=[dict(box_uid=n['uid'],scan_box=n['uid'],content_version=n['version'],origin='MANUAL_CONFIRMED',gross_weight_kg='10.1',measurement_ref='SYNTHETIC_TYPED_BOX_WEIGHT')for n in root['nodes']if n['kind']=='CONTAINER'and n['type']=='BOX'])
    quality=qa.expect(200,qa.http('GET','/api/outgoing-quality/'+tr['st_pallet']))
    prep=json.loads((OUT/'scoped-full-preparation.json').read_text(encoding='utf-8'))
    qa.step('reload_qc','/api/outgoing-quality/'+tr['st_pallet']+'/scan',dict(operation_id=s['tag']+'.reload.qc',expected_composition_signature=quality['composition_signature'],error_count=0,scans=prep['receipt_proof']['codes']))
    qa.step('old_B_cannot_load','/api/transport/loading/confirm',dict(body,operation_id=s['tag']+'.wrong_B',scan_vehicle=s['vehicles']['B']['number']),status=409)
    value=qa.step('reload_C','/api/transport/loading/confirm',body)
    assert qa.expect(200,qa.http('POST','/api/transport/loading/confirm',body))==value
    tr['reload_body']=body;tr['load_body']=s['requests']['load_with_tare']['body'];tr['loaded']=value
    (OUT/'transport.json').write_text(json.dumps(tr,indent=2),encoding='utf-8')
    s['status']='RELOADED_C_DOCUMENT_PENDING';qa.save()


def depart_c():
    from datetime import datetime,timezone
    tr=s['transport'];card=qa.step('composition_after_reload','/api/tradecase/order-compositions/report',dict(warehouse_id=s['warehouse'],order_id=tr['demand_order_id']))
    for system,sender in [('SAP','TC03.SAP'),('SKM','TC03.SKM')]:
        qa.step('composition_ack_C_'+system,'/api/tradecase/order-compositions/acknowledgments',dict(schema_version=1,warehouse_id=s['warehouse'],order_id=tr['demand_order_id'],system_code=system,sender_id=sender,event_id=s['tag']+'.ack.C.'+system,composition_no=card['composition_no'],signature=card['signature'],outcome='ACCEPTED',occurred_at=datetime.now(timezone.utc).isoformat()))
    nested.tare_handover()
    # A new physical load and vehicle cannot use vehicle B's accepted document.
    rejected=qa.step('old_document_departure_denied',f"/api/transport/loading/{tr['transport_task_id']}/depart",dict(operation_id=s['tag']+'.old_doc.depart'),status=409)
    assert 'TRADE_TRIP_BINDING_STALE' in json.dumps(rejected),rejected
    trip_document(s['vehicles']['C'],2)
    body=dict(operation_id=s['tag']+'.depart.C')
    value=qa.step('depart_C',f"/api/transport/loading/{tr['transport_task_id']}/depart",body)
    assert qa.expect(200,qa.http('POST',f"/api/transport/loading/{tr['transport_task_id']}/depart",body))==value
    qa.step('departed_blocks_A',f"/api/admin/transport/tasks/{tr['transport_task_id']}",dict(transport=s['vehicles']['A']['number']),method='PATCH',status=409)
    s['historical_tree']=nested.snapshot(s['root']);assert s['historical_tree']['historical_composition']
    s['status']='DEPARTED_C_TARE_RETURN_PENDING';qa.save()


if __name__=='__main__':
    stage=sys.argv[1]
    if s.get('status')=='PASS':
        print('Closed acceptance; no commands sent');sys.exit(0)
    try:
        if stage=='prepare':
            assert not s.get('status'),'Do not reopen a prepared fixture'
            nested.prepare();nested.pack();nested.prepare_transport()
        elif stage=='vehicles':vehicles()
        elif stage=='transport':
            assert s.get('warehouse') and s.get('root')
            nested.prepare_transport()
        elif stage=='load':accept_ui_and_load()
        elif stage=='unload':unload_change()
        elif stage=='reload':reload_c()
        elif stage=='depart':depart_c()
        elif stage=='finish':nested.finish()
        else:raise ValueError(stage)
    except Exception as exc:
        s['error']=str(exc);raise
    finally:
        qa.save()
        if nested.scoped.FILE.parent==OUT:nested.scoped.save()
        if nested.scoped.prep.FILE.parent==OUT:nested.scoped.prep.save()
    print(json.dumps(dict(status=s.get('status'),warehouse=s.get('warehouse'),trip=s.get('transport',{}).get('transport_task_id'))))
