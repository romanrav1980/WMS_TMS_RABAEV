"""Prepare the two picked CASEs as independently scannable BOXes on one pallet."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from full_pallet_fixture import prepare_shipment
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07';FILE=OUT/'bulk-packing.json'
source=json.loads((OUT/'bulk-source-state.json').read_text(encoding='utf-8'));f=source['fixture'];w=f['warehouse_id']
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(warehouse=w,cell=f['receive'],root='BULK22.PAL.'+str(w),requests={},results={},history=[],shipments={})


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def step(key,method,path,body):
    if key not in s['requests']:s['requests'][key]=dict(method=method,path=path,body=body);save()
    r=s['requests'][key]
    if key not in s['results']:s['results'][key]=expect(200,http(r['method'],r['path'],r['body']));save()
    return s['results'][key]


def read(uid):return expect(200,http('GET','/api/warehouse-hus/composition?identifier='+uid))


def create(uid,kind):
    return step('create.'+uid,'POST','/api/warehouse-hus/create',dict(operation_id=uid+'.create',identifier=uid,cell=s['cell'],warehouse=w,container_type=kind,tare_weight_kg='0.1',scan_container=uid,scan_cell=s['cell']))


def run():
    if 'staging_cell'not in s:
        cell='B22E'+str(w)
        with oracle_connection()as c:
            q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('select WARE_ID,IS_SYSTEM from RRL_CELLS where CELL=:cell',cell=cell);old=q.fetchone()
                if old:assert old==(w,1)
                else:
                    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:w,0,0,0,0,1,0,0)',cell=cell,w=w)
                    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
                c.commit()
            finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
        s['unused_empty_container']=s['root'];s['staging_cell']=cell;s['cell']=cell;s['root']='BULK22.PAL.STAGING.'+str(w);save()
    with oracle_connection()as c:
        q=c.cursor();q.execute('select VERSION_NO from RRL_TRADE_CELL_POLICY where WARE_ID=:w and CELL=:c',w=w,c=s['cell']);row=q.fetchone();version=row[0]if row else 0
    step('staging-policy','PUT',f"/api/tradecase/warehouses/{w}/stock/cells/{s['cell']}",dict(operation_id='BULK22.STAGING.POLICY',expected_version=version,zone_kind='EXPEDITION',reason='Isolated bulk box packing and loading acceptance'))
    step('restore-receive-policy','PUT',f"/api/tradecase/warehouses/{w}/stock/cells/{f['receive']}",dict(operation_id='BULK22.RESTORE.RECEIVE',expected_version=2,zone_kind='RECEIVE',reason='Restore receiving role after rejected ordinary-cell CASE movement'))
    create(s['root'],'PALLET')
    for i in range(2):
        case=json.loads((OUT/f'bulk-case-{i}.json').read_text(encoding='utf-8'));tid=case['case'];box=f'BULK22.BOX.{tid}'
        with oracle_connection()as c:
            q=c.cursor();q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=tid);carrier,version=q.fetchone()
        step('move.staging.'+str(tid),'POST',f'/api/case-pick/tasks/{tid}/move-carrier',dict(operation_id=f'BULK22.STAGING.MOVE.{tid}',scan_container=carrier,scanned_to_cell=s['cell'],expected_content_version=version))
        if str(tid)not in s['shipments']:
            result=prepare_shipment(dict(fixture=f,native_order=case['native_order'],shipment_identifier=f'BULK22.ST.{tid}',shipment_quantity=2))
            s['shipments'][str(tid)]=result;save()
        current=read('CASE:'+str(tid))
        step('bind.'+str(tid),'POST',f'/api/case-pick/tasks/{tid}/bind-shipment',dict(pallet_identifier=s['shipments'][str(tid)]['shipment_identifier'],scan_container=carrier,expected_content_version=current['nodes'][0]['version']))
        create(box,'BOX');parent,child=read(box),read('CASE:'+str(tid))
        step('pack.'+str(tid),'POST','/api/warehouse-hus/attach-case',dict(operation_id=f'BULK22.PACK.{tid}',identifier=box,child_case_task_id=tid,expected_version=parent['nodes'][0]['version'],expected_child_version=child['nodes'][0]['version'],scan_container=box,scan_child=carrier,retained_tare_booking_operation_id=case['tare_book']['operation_id']))
        parent,child=read(s['root']),read(box)
        step('pallet.'+str(tid),'POST','/api/warehouse-hus/attach',dict(operation_id=f'BULK22.PALLET.{tid}',identifier=s['root'],child_uid=box,expected_version=parent['nodes'][0]['version'],expected_child_version=child['nodes'][0]['version'],scan_container=s['root'],scan_child=box))
    s['snapshot']=read(s['root']);assert s['snapshot']['physical_unit_count']==4 and len(s['snapshot']['nodes'])==7
    s['status']='PACKED_TWO_BOXES';save();print(json.dumps(dict(status=s['status'],root=s['root'],unit_count=4)))


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:run()
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
