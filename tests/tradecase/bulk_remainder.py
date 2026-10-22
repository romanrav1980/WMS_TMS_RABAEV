"""Two independent shipments to ONE recipient; reuse owned stock and native writers."""
import json, os, re, sys, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import bulk_small_case as small
import live_factory_case as case
from full_pallet_fixture import prepare_shipment
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07'
FILE=OUT/'bulk-remainder.json'
f=json.loads((OUT/'bulk-source-state.json').read_text(encoding='utf-8'))['fixture']
old=json.loads((OUT/'manual-tare-live.json').read_text(encoding='utf-8'))
w=f['warehouse_id'];assert w==220793322 and f['article']=='TC03A4B16ACD'
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(warehouse=w,root='NB22.PAL.'+str(w),cell='B22E'+str(w),requests={},results={},history=[],cases={})


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def step(key,path,body):
    if key not in s['requests']:s['requests'][key]=dict(path=path,body=body);save()
    r=s['requests'][key]
    if key not in s['results']:s['results'][key]=expect(200,http('POST',r['path'],r['body']));save()
    return s['results'][key]


def tree(uid):return expect(200,http('GET','/api/warehouse-hus/composition?identifier='+uid))


def prepare():
    with oracle_connection()as c:
        q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=w);assert q.fetchone()==('TRADECASE QA '+f['tag'],)
    for suffix in ['A','B']:
        case.OUT=OUT;case.FILE=OUT/f'bulk-remainder-{suffix}.json';case.w=w;case.base=f'/api/tradecase/warehouses/{w}';case.tag=f'NB22.{suffix}.{w}'
        case.s=json.loads(case.FILE.read_text(encoding='utf-8'))if case.FILE.exists()else dict(warehouse_id=w,article=f['article'],pick=f['pick'],quantity=1,customer=old['customer'],recipient=old['recipient'],recipient_id=f'MT22.{w}.RECIPIENT',face=old['face'],face_article=old['face_article'],cpt_policy=old['cpt_policy'],history=[])
        start=len(CALLS)
        try:
            small.prepare()
            if 'tare_count'not in case.s:
                balances=expect(200,http('GET',f'/api/inventory/tare/warehouses/{w}/balances'))
                balance=next(b for b in balances if b['pallet_type_id']==case.s['pallet_type_id']and b['custodian_kind']=='WAREHOUSE'and b['condition_code']=='GOOD')
                case.step('tare_count','/api/inventory/tare/count',dict(operation_id=case.tag+'.tare.count',owner_ware_id=w,pallet_type_id=case.s['pallet_type_id'],condition='GOOD',observed_quantity=str(int(balance['quantity'])+1),expected_version=balance['balance_version'],reason='Additional synthetic carton for same-recipient remainder test',decision_reference='TEST_FIXTURE_NOT_HARDWARE:'+case.tag))
            if not case.s.get('small_picker_retired'):case.start();small.pick()
            tid=case.s['case'];base=f'/api/case-pick/tasks/{tid}';current=tree('CASE:'+str(tid));carrier=current['nodes'][0]['identifier']if 'identifier'in current['nodes'][0]else case.s['small_label']['sscc']
            step('move.'+suffix,base+'/move-carrier',dict(operation_id=case.tag+'.move',scan_container=carrier,scanned_to_cell=s['cell'],expected_content_version=current['nodes'][0]['version']))
            if suffix not in s['cases']:
                st_number=f'N22{suffix}.{w}'
                shipment=prepare_shipment(dict(fixture=f,native_order=case.s['native_order'],shipment_identifier=f'NB22.ST.{tid}',shipment_quantity=1,st_number=st_number))
                s['cases'][suffix]=dict(case_id=tid,carrier=carrier,st_number=st_number,shipment=shipment,native_order=case.s['native_order'],tare_book=case.s['tare_book']['operation_id'],scans=case.s['pick_body']['unit_scans']);save()
            step('bind.'+suffix,base+'/bind-shipment',dict(pallet_identifier=s['cases'][suffix]['shipment']['shipment_identifier'],scan_container=carrier,expected_content_version=tree('CASE:'+str(tid))['nodes'][0]['version']))
            path='/api/outgoing-quality/'+carrier
            if 'scan.'+suffix not in s['results']:
                qc=expect(200,http('GET',path));step('scan.'+suffix,path+'/scan',dict(operation_id=case.tag+'.scan',expected_composition_signature=qc['composition_signature'],error_count=0,scans=s['cases'][suffix]['scans']))
            if 'weight.'+suffix not in s['results']:
                qc=expect(200,http('GET',path));step('weight.'+suffix,path+'/weight',dict(operation_id=case.tag+'.weight',expected_composition_signature=qc['composition_signature'],quality_kind='WEIGHT',gross_weight='1.1',wood_weight='0.1',measurement_origin='MANUAL_CONFIRMED'))
        finally:
            case.s['history']+=CALLS[start:];case.save()
    step('create','/api/warehouse-hus/create',dict(operation_id=s['root']+'.create',identifier=s['root'],cell=s['cell'],warehouse=w,container_type='PALLET',tare_weight_kg='0.1',scan_container=s['root'],scan_cell=s['cell']))
    for suffix,child in s['cases'].items():
        parent,current=tree(s['root']),tree('CASE:'+str(child['case_id']))
        step('attach.'+suffix,'/api/warehouse-hus/attach-case',dict(operation_id=f'NB22.ATTACH.{suffix}.{w}',identifier=s['root'],child_case_task_id=child['case_id'],expected_version=parent['nodes'][0]['version'],expected_child_version=current['nodes'][0]['version'],scan_container=s['root'],scan_child=child['carrier'],retained_tare_booking_operation_id=child['tare_book']))
    s['packed']=tree(s['root']);assert s['packed']['physical_unit_count']==2
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);s['stock_prepared']=list(q.fetchone());assert s['stock_prepared']==[8,6]
        q.execute('select count(*)from user_objects where STATUS=\'INVALID\'');assert q.fetchone()[0]==0
    s['status']='TWO_CARTONS_SAME_RECIPIENT_PACKED_NOT_LOADED';save()
    print(json.dumps(dict(status=s['status'],stock=s['stock_prepared'],cases=s['cases'])))


def transport():
    path=OUT/'bulk-remainder-trip.json'
    if not path.exists():path.write_text(json.dumps(dict(warehouse_id=w,case_id=s['cases']['A']['case_id'],st_number=s['cases']['A']['st_number'],vehicle_number='N22VA1168',dock='N22DA1168',shipment_date='2026-10-22',http=[])),encoding='utf-8')
    subprocess.run([sys.executable,str(Path(__file__).with_name('prepare_transport_task.py'))],env=dict(os.environ,TRADECASE_TRANSPORT_FIXTURE=str(path)),check=True)
    s['trip']=json.loads(path.read_text(encoding='utf-8'));save()
    trip=s['trip'];tid=trip['transport_task_id']
    step('assign.B',f'/api/admin/transport/tasks/{tid}/sts',dict(st_numbers=[s['cases']['B']['st_number']]))
    if 'target_trip'not in s:
        s['target_trip']=step('target_trip','/api/admin/transport/tasks',dict(transtype='10',shipment_date='2026-10-23'))['task_id'];save()
    if 'profile'not in s['results']:
        profile=expect(200,http('GET',f"/api/admin/transport/vehicles/{trip['vehicle_id']}/profile"))
        step('profile','/api/admin/transport/vehicle-profiles',dict(operation_id='NB22.VEHICLE.PROFILE',vehicle_id=trip['vehicle_id'],expected_source_hash=profile['base_hash'],vehicle_size_class='QA_VAN',cargo_length_mm=3000,cargo_width_mm=2400,cargo_height_mm=2400,outer_height_mm=3000,outer_length_mm=6000,expected_version=profile['version'],floor_variants=[dict(code='QA_CARTONS',limits=[dict(pallet_type_id=33,max_places=4)])],reason='Synthetic same-recipient remainder fixture',evidence_reference='TEST_FIXTURE_NOT_HARDWARE:NB22'))
    print(json.dumps(dict(source_trip=tid,target_trip=s['target_trip'])))


def load():
    if s.get('qa_retired'):
        assert 'load.A'in s['results'];return
    import bulk_loading as shipping
    shipping.FILE=FILE;shipping.s=s
    child=s['cases']['A'];carrier=child['carrier'];trip=s['trip']
    if 'detach.A'not in s['results']:
        parent,current=tree(s['root']),tree('CASE:'+str(child['case_id']))
        step('detach.A','/api/warehouse-hus/detach-case',dict(operation_id='NB22.DETACH.A',identifier=s['root'],child_case_task_id=child['case_id'],expected_version=parent['nodes'][0]['version'],expected_child_version=current['nodes'][0]['version'],scan_container=s['root'],scan_child=carrier,reason='Load one carton, retain the other shipment for the next trip'))
    name,password=shipping.actor()
    if not s.get('owner_granted'):shipping.owner(True,True);s['owner_granted']=True;save()
    path='/api/outgoing-quality/'+carrier
    for key,suffix,payload in [('free.scan','/scan',dict(error_count=0,scans=child['scans'])),('free.weight','/weight',dict(quality_kind='WEIGHT',gross_weight='1.1',wood_weight='0.1',measurement_origin='MANUAL_CONFIRMED'))]:
        if key not in s['results']:
            qc=expect(200,http('GET',path));step(key,path+suffix,dict(operation_id='NB22.'+key,expected_composition_signature=qc['composition_signature'],**payload))
    if 'load.A'not in s['requests']:
        preview=expect(200,http('GET','/api/transport/loading/bulk-box-preview?identifier='+carrier,actor=name,password=password))
        assert preview['source_kind']=='SINGLE';snapshot=preview['snapshot'];version=snapshot['nodes'][0]['version']
        s['requests']['load.A']=dict(path='/api/transport/loading/confirm-bulk-box',body=dict(operation_id='NB22.LOAD.A',source_kind='SINGLE',identifier=preview['identifier'],expected_version=version,expected_composition_signature=preview['composition_signature'],scan_container=carrier,scan_cell=snapshot['cell'],transport_task_id=trip['transport_task_id'],scan_vehicle=trip['vehicle_number'],scan_dock=trip['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=version,gross_weight_kg='1.1',width_m='0.4',depth_m='0.5',height_m='0.5')));save()
    request=s['requests']['load.A']
    result=expect(200,http('POST',request['path'],request['body'],name,password))
    assert expect(200,http('POST',request['path'],request['body'],name,password))==result
    s['results']['load.A']=result;save()
    shipping.owner(False,False)
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=name);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=name);c.commit()
        q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);s['stock_loaded']=list(q.fetchone());assert s['stock_loaded']==[7,5]
    s['qa_retired']=True;s['remaining']=tree(s['root']);assert s['remaining']['physical_unit_count']==1
    s['status']='ONE_LOADED_ONE_RETAINED_NOT_DEFERRED';save();print(json.dumps(dict(status=s['status'],stock=s['stock_loaded'])))


def defer():
    st=s['cases']['B']['st_number'];path='/api/transport/st-deferrals'
    if 'defer.B'not in s['requests']:
        context=expect(200,http('GET',path+'/context?st_number='+st));s['deferral_context']=context
        assert context['physical_preparation']['state']=='PREPARED_HU'
        assert context['source_trip_id']==s['trip']['transport_task_id']
        s['requests']['defer.B']=dict(path=path,body=dict(operation_id='NB22.DEFER.B',st_number=st,target_trip_id=s['target_trip'],expected_version=context['version'],source_hash=context['source_hash'],reason='Retain the second shipment at the warehouse for the next trip',reference='SYNTHETIC_SAME_RECIPIENT_REMAINDER:NB22'));save()
    request=s['requests']['defer.B'];result=step('defer.B',request['path'],request['body'])
    assert expect(200,http('POST',path,request['body']))==result
    assert result['stock_changed']is False and result['original_demand_changed']is False
    s['after_deferral']=expect(200,http('GET',path+'/context?st_number='+st));save()
    s['status']='REMAINDER_ASSIGNED_NEXT_TRIP_PHYSICAL_WAIT_PENDING';save();print(json.dumps(dict(status=s['status'],decision=result)))


def waiting():
    cell='N22W'+str(w)
    if 'wait_cell_seeded'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('select WARE_ID,IS_SYSTEM from RRL_CELLS where CELL=:cell',cell=cell);existing=q.fetchone()
                if existing:assert existing==(w,0)
                else:
                    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:w,0,0,0,0,0,0,0)',cell=cell,w=w)
                    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
                c.commit()
            finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
        s['wait_cell_seeded']=cell;save()
    if 'wait_policy'not in s:
        s['wait_policy']=expect(200,http('PUT',f'/api/tradecase/warehouses/{w}/stock/cells/{cell}',dict(operation_id='NB22.WAIT.POLICY',expected_version=0,zone_kind='WAIT',reason='Isolated next-trip warehouse waiting area')));save()
    if 'wait_settings'not in s:
        path=f'/api/receiving/warehouses/{w}/settings';settings=expect(200,http('GET',path));s['settings_before_wait']=settings;save()
        fields=['company_prefix','extension_digit','coordinate_unit_m','reachtruck_mps','lift_mps','placement_metric','hu_cell_height_unit','outgoing_qc_mode','outgoing_qc_independent','outgoing_qc_sample_percent']
        body={key:settings[key]for key in fields};body['defer_wait_cell']=cell
        s['wait_settings']=expect(200,http('PUT',path,body));save()
    result=step('wait_plan','/api/receiving/st-deferrals/waiting-tasks',dict(operation_id='NB22.WAIT.PLAN.B',decision_operation_id='NB22.DEFER.B',root_identifier=s['root']))
    s['status']='REMAINDER_WAIT_TASK_PLANNED';save();print(json.dumps(dict(status=s['status'],plan=result)))


def complete_wait():
    task=s['results']['wait_plan']['task_id'];path=f'/api/warehouse-tasks/{task}/complete'
    if 'wait_complete'not in s['requests']:
        detail=expect(200,http('GET',f'/api/warehouse-tasks/{task}'))
        s['requests']['wait_complete']=dict(path=path,body=dict(operation_id='NB22.WAIT.COMPLETE.B',scanned_pallet=s['root'],scanned_from_cell=s['cell'],scanned_to_cell=s['wait_cell_seeded'],fact_qty='1',expected_task_signature=detail['task_signature']));save()
    r=s['requests']['wait_complete'];result=step('wait_complete',path,r['body'])
    assert expect(200,http('POST',path,r['body']))==result
    s['wait_snapshot']=tree(s['root']);assert s['wait_snapshot']['cell']==s['wait_cell_seeded']and s['wait_snapshot']['physical_unit_count']==1
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w);s['stock_waiting']=list(q.fetchone());assert s['stock_waiting']==[7,5]
    s['status']='REMAINDER_PHYSICALLY_WAITING_NEXT_TRIP';save();print(json.dumps(dict(status=s['status'],stock=s['stock_waiting'],result=result)))


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        if '--transport'in sys.argv:transport()
        elif '--load'in sys.argv:load()
        elif '--defer'in sys.argv:defer()
        elif '--waiting'in sys.argv:waiting()
        elif '--complete-wait'in sys.argv:complete_wait()
        else:prepare()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
