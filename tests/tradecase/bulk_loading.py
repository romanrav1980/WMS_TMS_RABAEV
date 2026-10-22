"""Load one explicit BOX and retain its sibling; synthetic measures, real Oracle facts."""
import json
import os
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07';FILE=OUT/'bulk-loading.json'
trip=json.loads((OUT/'bulk-transport.json').read_text(encoding='utf-8'))
packing=json.loads((OUT/'bulk-packing.json').read_text(encoding='utf-8'))
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(status='IN_PROGRESS',warehouse=trip['warehouse_id'],requests={},results={},history=[])


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def step(key,method,path,body,actor=None,password=None,expected=200):
    if key not in s['requests']:s['requests'][key]=dict(method=method,path=path,body=body);save()
    r=s['requests'][key]
    if key not in s['results']:s['results'][key]=expect(expected,http(r['method'],r['path'],r['body'],actor,password));save()
    return s['results'][key]


def read(uid,actor=None,password=None):
    return expect(200,http('GET','/api/warehouse-hus/composition?identifier='+uid,actor=actor,password=password))


def prepare():
    if 'profile'not in s['results']:
        profile=expect(200,http('GET',f"/api/admin/transport/vehicles/{trip['vehicle_id']}/profile"))
        step('profile','POST','/api/admin/transport/vehicle-profiles',dict(operation_id='BULK22.VEHICLE.PROFILE',vehicle_id=trip['vehicle_id'],expected_source_hash=profile['base_hash'],vehicle_size_class='QA_VAN',cargo_length_mm=3000,cargo_width_mm=2400,cargo_height_mm=2400,outer_height_mm=3000,outer_length_mm=6000,expected_version=profile['version'],floor_variants=[dict(code='QA_TWO_EURO',limits=[dict(pallet_type_id=1,max_places=2)])],reason='Synthetic isolated bulk fixture, no road vehicle claim',evidence_reference='TEST_FIXTURE_NOT_HARDWARE:BULK22'))
    if 'detach'not in s['results']:
        root,box=read(packing['root']),read('BULK22.BOX.1161')
        step('detach','POST','/api/warehouse-hus/detach',dict(operation_id='BULK22.FREE.BOX.1161',identifier=packing['root'],child_uid=box['root'],expected_version=root['nodes'][0]['version'],expected_child_version=box['nodes'][0]['version'],scan_container=packing['root'],scan_child=box['root'],reason='Dismantle source pallet before scanning one bulk-loaded box'))
    for i in range(2):
        c=json.loads((OUT/f'bulk-case-{i}.json').read_text(encoding='utf-8'));key='qc.'+str(c['case'])
        if key in s['results']:continue
        carrier=c['pick_body']['scan_container'];path='/api/outgoing-quality/'+carrier
        quality=expect(200,http('GET',path))
        step(key,'POST',path+'/scan',dict(operation_id='BULK22.QC.'+str(c['case']),expected_composition_signature=quality['composition_signature'],error_count=0,scans=c['pick_body']['unit_scans']))
        assert expect(200,http('GET',path))['ready']


def actor():
    if 'actor'not in s:
        name='BL22'+uuid4().hex[:10];password=secrets.token_hex(24)
        with oracle_connection()as c:
            q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Bulk box shipping QA','TC03QA',222823304,0,1)",a=name,p=password)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Bulk box shipping QA',1,1)",a=name)
            for permission in ['stock_posting_shipping','warehouse_task_view','transport_dispatch_view']:
                q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=name,p=permission)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '4'hour,'admin','Isolated bulk box native acceptance',1)",a=name,w=str(s['warehouse']));c.commit()
        s['actor']=name;save()
    with oracle_connection()as c:
        q=c.cursor();q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=s['actor']);row=q.fetchone();assert row,'Do not reactivate a retired QA user'
        q.execute("select RRL_HAS_WRIGHT(:a,'stock_posting_shipping'),RRL_ACCESS_API.allowed(:a,'stock_posting_shipping','WAREHOUSE',:w)from dual",a=s['actor'],w=str(s['warehouse']));assert q.fetchone()==(0,1)
    return s['actor'],row[0]


def owner(view,operate):
    with oracle_connection()as c:
        q=c.cursor();q.execute('select VERSION_NO from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=:w and OWNER_ID=\'SNS\'',a=s['actor'],w=s['warehouse']);row=q.fetchone();version=row[0]if row else 0
    return step('owner.'+str(version),'PUT',f"/api/tradecase/warehouses/{s['warehouse']}/stock/owner-grants",dict(operation_id=s['actor']+'.owner.'+str(version),expected_version=version,username=s['actor'],owner_id='SNS',can_view=view,can_operate=operate,reason='Verify current owner authority on bulk loading and cached replies'))


def run():
    prepare();name,password=actor()
    if 'owner-granted'not in s:owner(True,True);s['owner-granted']=True;save()
    if 'load'not in s['requests']:
        box=read('BULK22.BOX.1161',name,password);v=box['nodes'][0]['version']
        s['requests']['load']=dict(method='POST',path='/api/transport/loading/confirm-bulk-box',body=dict(operation_id='BULK22.LOAD.BOX.1161',identifier=box['root'],expected_version=v,scan_container=box['root'],scan_cell=box['cell'],transport_task_id=trip['transport_task_id'],scan_vehicle=trip['vehicle_number'],scan_dock=trip['dock'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=v,gross_weight_kg='2.2',width_m='0.4',depth_m='0.5',height_m='0.5'),physical_boxes=[dict(box_uid=box['root'],scan_box=box['root'],content_version=v,origin='MANUAL_CONFIRMED',gross_weight_kg='2.2',measurement_ref='SYNTHETIC_MANUAL_BOX:BULK22.1161')]));save()
    request=s['requests']['load'];body=request['body']
    result=step('load','POST',request['path'],body,name,password)
    assert expect(200,http('POST',request['path'],body,name,password))==result
    changed=dict(body,measurements=dict(body['measurements'],height_m='0.6'))
    conflict=expect(409,http('POST',request['path'],changed,name,password));assert conflict['detail']['outcome_confirmed']is False
    if 'revoked'not in s:owner(True,False);s['revoked']=True;save()
    denied=expect(403,http('POST',request['path'],body,name,password));assert denied['detail']['outcome_confirmed']is False
    if 'restored'not in s:owner(True,True);s['restored']=True;save()
    assert expect(200,http('POST',request['path'],body,name,password))==result
    sibling=read(packing['root'],name,password);assert sibling['physical_unit_count']==2
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse']);s['stock']=list(q.fetchone());assert s['stock']==[8,2]
        q.execute('select ROOT_UID,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o',o=body['operation_id']);assert q.fetchone()==('BULK22.BOX.1161','LOADED')
    owner(False,False)
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=name);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=name);c.commit()
    s.update(status='PASS',sibling=sibling,qa_retired=True,measurements='SYNTHETIC_MANUAL_NOT_HARDWARE',provider='NO_EXTERNAL_BOX_ACK');save()
    print(json.dumps(dict(status=s['status'],actor=name,stock=s['stock'],trip=trip['transport_task_id'])))


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:run()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
