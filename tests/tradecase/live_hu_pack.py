"""Retained TRADECASE SORT lot: zero-quantity nested packing and exact retries."""
import json
import os
from pathlib import Path
import re
import sys
import secrets
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T06'
STATE=OUT/'hu-pack-state.json'
os.environ['TRADECASE_ADMIN_USER']='admin'
os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]


def save(value):STATE.write_text(json.dumps(value,indent=2,default=str),encoding='utf-8')


def composition(uid):return expect(200,http('GET','/api/warehouse-hus/composition?identifier='+uid))


def prepare():
    assert not STATE.exists(),'Use the retained state, never create the same fixture twice'
    with oracle_connection()as c:
        q=c.cursor();q.execute("select r.UID_POLETA,r.CELL,r.REMAIN from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=219023232 and r.REMAIN=3");rows=q.fetchall();assert len(rows)==1
        uid,cell,qty=rows[0]
    tag='HU22'+uuid4().hex[:10]
    state=dict(tag=tag,warehouse=219023232,stock_uid=uid,cell=cell,quantity=qty,containers=[],calls=[])
    save(state)
    for level in ['PALLET','BOX','BOX']:
        target=tag+'.'+str(len(state['containers']))
        body=dict(operation_id=target+'.create',identifier=target,cell=cell,warehouse=state['warehouse'],
                  container_type=level,tare_weight_kg='0.1',scan_container=target,scan_cell=cell)
        result=expect(200,http('POST','/api/warehouse-hus/create',body))
        state['containers'].append(dict(uid=target,result=result));save(state)
    inner=state['containers'][-1]['uid']
    parent,child=composition(inner),composition(uid)
    state['parent_snapshot']=parent;state['child_snapshot']=child
    body=dict(operation_id=tag+'.stock.attach',identifier=inner,child_uid=uid,
              expected_version=parent['nodes'][0]['version'],expected_child_version=child['nodes'][0]['version'],
              scan_container=inner,scan_child=uid)
    state['first_attach']=body;save(state)
    denial=http('POST','/api/warehouse-hus/attach',body)
    assert denial[0]==409 and 'TRADE_ORDER_BINDING_REQUIRED' in json.dumps(denial),denial
    state.update(baseline_denial=denial,calls=list(CALLS),prepared=True);save(state)
    print(json.dumps(dict(status='PREPARED',tag=tag,denial=denial[0],stock_quantity=qty)))


def verify():
    s=json.loads(STATE.read_text(encoding='utf-8'));assert s['prepared'] and not s.get('verified')
    actor='HP22'+uuid4().hex[:10];pwd=secrets.token_hex(24);version=0;created=False
    report=dict(status='FAIL',actor=actor,checks=[],calls=[])
    owner_url='/api/tradecase/warehouses/219023232/stock/owner-grants'
    def grant(view,operate):
        nonlocal version
        expect(200,http('PUT',owner_url,dict(operation_id=actor+'.owner.'+str(version),expected_version=version,
            username=actor,owner_id='SNS',can_view=view,can_operate=operate,reason='Native nested packing and owner revoke acceptance')))
        version+=1
    def read(uid):return expect(200,http('GET','/api/warehouse-hus/composition?identifier='+uid,actor=actor,password=pwd))
    def link(parent,child,key):
        p,ch=read(parent),read(child)
        return dict(operation_id=actor+'.'+key,identifier=parent,child_uid=child,
                    expected_version=p['nodes'][0]['version'],expected_child_version=ch['nodes'][0]['version'],
                    scan_container=parent,scan_child=child)
    def command(kind,body):return http('POST','/api/warehouse-hus/'+kind,body,actor,pwd)
    try:
        with oracle_connection()as c:
            q=c.cursor()
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'TRADECASE nested pack QA','TC03QA',222823304,0,1)",a=actor,p=pwd)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'TRADECASE nested pack QA',1,1)",a=actor)
            for permission in ['warehouse_task_view','warehouse_task_execute']:
                q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=actor,p=permission)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE','219023232','CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Native nested pack acceptance',1)",a=actor);c.commit();created=True
            q.execute("select RRL_HAS_WRIGHT(:a,'warehouse_task_execute'),RRL_ACCESS_API.allowed(:a,'warehouse_task_execute','WAREHOUSE','219023232')from dual",a=actor);assert q.fetchone()==(0,1)
        stock=s['stock_uid'];outer,middle,inner=[x['uid']for x in s['containers']]
        expect(403,http('GET','/api/warehouse-hus/composition?identifier='+stock,actor=actor,password=pwd))
        grant(True,False);assert read(stock)['physical_unit_count']==3
        body=link(inner,stock,'stock.attach');expect(403,command('attach',body))
        grant(True,True);receipt=expect(200,command('attach',body));assert expect(200,command('attach',body))==receipt
        expect(409,command('attach',dict(body,reason='Changed content of an existing operation')))
        grant(False,False)
        expect(403,http('GET','/api/warehouse-hus/composition?identifier='+inner,actor=actor,password=pwd))
        expect(403,command('attach',body));grant(True,True)
        assert expect(200,command('attach',body))==receipt
        expect(200,command('attach',link(middle,inner,'middle.attach')))
        expect(200,command('attach',link(outer,middle,'outer.attach')))
        tree=read(outer);assert tree['physical_unit_count']==3 and tree['leaf_count']==1 and len(tree['nodes'])==4
        assert sorted(x['depth']for x in tree['nodes'])==[0,1,2,3]
        report['nested_tree']=tree
        expect(409,command('attach',link(inner,outer,'cycle')))
        expect(409,command('attach',link(outer,middle,'double-parent')))
        expect(409,command('attach',dict(body,operation_id=actor+'.stale')))
        detach=dict(link(outer,middle,'race'),reason='Unpack nested test tree')
        candidates=[dict(detach,operation_id=detach['operation_id']+'.'+str(i))for i in range(2)]
        with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(lambda b:command('detach',b),candidates))
        assert sorted(x[0]for x in responses)==[200,409],responses
        winner=next(i for i,r in enumerate(responses)if r[0]==200)
        assert expect(200,command('detach',candidates[winner]))==responses[winner][1]
        for parent,child,key in [(middle,inner,'middle.detach'),(inner,stock,'stock.detach')]:
            result=expect(200,command('detach',dict(link(parent,child,key),reason='Restore original physical test grouping')))
            assert result
        assert not read(stock)['ancestors']
        assert all(read(x)['physical_unit_count']==0 for x in [outer,middle,inner])
        report['checks']=['current scoped warehouse; legacy execute0','owner-view and owner-operate separated',
            'nested PALLET/BOX/BOX/STOCK depth3','same operation exact replay before and after permission restore',
            'owner revoke blocks read and replay','cycle, duplicate parent and stale versions rejected',
            'two simultaneous detach commands: one200, one409; winner exact replay','all links detached; original grouping restored']
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        expect(403,http('GET','/api/warehouse-hus/composition?identifier='+stock,actor=actor,password=pwd))
        with oracle_connection()as c:
            q=c.cursor();q.execute('select r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=219023232 and r.REMAIN>0 order by r.REMAIN');assert q.fetchall()==[(2,0),(3,0),(5,0)]
        report['status']='PASS';s['verified']=True
    finally:
        if created:
            if version:grant(False,False)
            with oracle_connection()as c:
                q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        report['calls']=list(CALLS);s['verification']=report;save(s)
        (OUT/'hu-pack-result.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=report['checks'],http_calls=len(CALLS))))


if __name__=='__main__':
    verify()if '--verify'in sys.argv else prepare()
