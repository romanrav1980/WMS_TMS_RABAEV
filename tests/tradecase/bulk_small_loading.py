"""Native physical CASE-carton bulk load; manual synthetic measurements, not hardware."""
import json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
from full_pallet_fixture import prepare_shipment
import bulk_loading as shipping
OUT=shipping.OUT;FILE=OUT/'bulk-small-loading.json'
small=json.loads((OUT/'bulk-small-case.json').read_text(encoding='utf-8'))
f=json.loads((OUT/'bulk-source-state.json').read_text(encoding='utf-8'))['fixture']
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(status='IN_PROGRESS',requests={},results={},history=[])
shipping.FILE=FILE;shipping.s=s;s.setdefault('warehouse',f['warehouse_id']);s.setdefault('actor','BL2286cdb38dcf')
step=shipping.step;save=shipping.save

def run():
    tid=small['case'];base=f'/api/case-pick/tasks/{tid}'
    with oracle_connection()as c:
        q=c.cursor();q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=tid);carrier,version=q.fetchone()
    if 'move'not in s['results']:step('move','POST',base+'/move-carrier',dict(operation_id=f'BS22.MOVE.{tid}',scan_container=carrier,scanned_to_cell=shipping.packing['cell'],expected_content_version=version))
    if 'shipment'not in s:
        s['shipment']=prepare_shipment(dict(fixture=f,native_order=small['native_order'],shipment_identifier=f'BS22.ST.{tid}',shipment_quantity=2));save()
    if 'bind'not in s['results']:
        tree=shipping.read('CASE:'+str(tid));step('bind','POST',base+'/bind-shipment',dict(pallet_identifier=s['shipment']['shipment_identifier'],scan_container=carrier,expected_content_version=tree['nodes'][0]['version']))
    trip=shipping.trip
    step('assign','POST',f"/api/admin/transport/tasks/{trip['transport_task_id']}/sts",dict(st_numbers=['FP.'+str(f['warehouse_id'])]))
    path=f"/api/sku-quality-weight/{f['warehouse_id']}/{f['article']}"
    if 'weight_policy'not in s['results']:
        policy=expect(200,http('GET',path));s['old_weight_policy']=policy;save()
        step('weight_policy','PUT',path,dict(expected_version=policy['version'],base_uom='EA',base_weight_kg='1',box_weight_kg='10'))
    path='/api/outgoing-quality/'+carrier
    if 'scan_qc'not in s['results']:
        quality=expect(200,http('GET',path));step('scan_qc','POST',path+'/scan',dict(operation_id=f'BS22.SCAN.{tid}',expected_composition_signature=quality['composition_signature'],error_count=0,scans=small['pick_body']['unit_scans']))
    if 'weight_qc'not in s['results']:
        quality=expect(200,http('GET',path));step('weight_qc','POST',path+'/weight',dict(operation_id=f'BS22.WEIGHT.{tid}',expected_composition_signature=quality['composition_signature'],quality_kind='WEIGHT',gross_weight='2.1',wood_weight='0.1',measurement_origin='MANUAL_CONFIRMED'))
    if 'carton_vehicle_profile'not in s['results']:
        profile=expect(200,http('GET',f"/api/admin/transport/vehicles/{trip['vehicle_id']}/profile"))
        original=json.loads((OUT/'bulk-loading.json').read_text(encoding='utf-8'))['requests']['profile']['body']
        body=dict(original,operation_id='BS22.CARTON.PROFILE',expected_version=profile['version'],expected_source_hash=profile['base_hash'],floor_variants=original['floor_variants']+[dict(code='QA_TWO_CARTONS',limits=[dict(pallet_type_id=small['pallet_type_id'],max_places=2)])])
        step('carton_vehicle_profile','POST','/api/admin/transport/vehicle-profiles',body)
    name,password=shipping.actor()
    preview=expect(200,http('GET','/api/transport/loading/bulk-box-preview?identifier='+carrier,actor=name,password=password));s['preview']=preview;save()
    assert preview['source_kind']=='SINGLE';tree=preview['snapshot'];version=tree['nodes'][0]['version']
    if 'load'not in s['requests']:
        s['requests']['load']=dict(method='POST',path='/api/transport/loading/confirm-bulk-box',body=dict(operation_id=f'BS22.LOAD.{tid}',source_kind='SINGLE',identifier=preview['identifier'],expected_version=version,expected_composition_signature=preview['composition_signature'],scan_container=carrier,scan_cell=tree['cell'],transport_task_id=trip['transport_task_id'],scan_vehicle=trip['vehicle_number'],scan_dock=trip['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=version,gross_weight_kg='2.1',width_m='0.4',depth_m='0.5',height_m='0.5')));save()
    body=s['requests']['load']['body'];path=s['requests']['load']['path'];result=step('load','POST',path,body,name,password)
    assert expect(200,http('POST',path,body,name,password))==result
    changed=dict(body,measurements=dict(body['measurements'],height_m='0.6'));assert expect(409,http('POST',path,changed,name,password))['detail']['outcome_confirmed']is False
    shipping.owner(True,False)
    assert expect(403,http('POST',path,body,name,password))['detail']['outcome_confirmed']is False
    shipping.owner(True,True);assert expect(200,http('POST',path,body,name,password))==result
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse']);s['stock']=list(q.fetchone());assert s['stock']==[8,4],s['stock']
        q.execute('select ROOT_UID,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o',o=body['operation_id']);s['load_fact']=list(q.fetchone());assert s['load_fact'][1]=='LOADED'
    shipping.owner(False,False)
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=name);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=name);c.commit()
    s.update(status='PASS',qa_retired=True,measurements='SYNTHETIC_MANUAL_NOT_HARDWARE',provider='NO_EXTERNAL_ACK');save();print(json.dumps(dict(status=s['status'],stock=s['stock'],trip=trip['transport_task_id'])))

if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:run()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
