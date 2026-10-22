"""Live scoped replay, revocation and race on an empty owned carton; cancel without picking."""
from concurrent.futures import ThreadPoolExecutor
import json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import live_factory_case as case
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07';FILE=OUT/'manual-tare-live.json'
f=json.loads((OUT/'bulk-source-state.json').read_text(encoding='utf-8'))['fixture']
old=json.loads((OUT/'bulk-small-case.json').read_text(encoding='utf-8'))
case.OUT=OUT;case.FILE=FILE;case.w=f['warehouse_id'];case.base=f"/api/tradecase/warehouses/{case.w}";case.tag='MT22.'+str(case.w)
case.s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(warehouse_id=case.w,article=f['article'],pick=f['pick'],face=old['face'],cpt_policy=old['cpt_policy'],history=[],checks=[])
s=case.s;step=case.step;save=case.save


def prepare():
    case.prepare();s['pallet_type_id']=old['pallet_type_id'];save()
    base=f"/api/case-pick/tasks/{s['case']}"
    if 'type_body'not in s:
        current=expect(200,http('GET',base+'/pallet-type'));assert current['can_change_empty_type']
        s['type_body']=dict(operation_id=case.tag+'.type',pallet_type_id=s['pallet_type_id'],expected_version=current['version'],scan_container=current['sscc'],reason='Select actual empty carton for manual tare acceptance');save()
    step('type',base+'/pallet-type',s['type_body'])
    if 'tare_count'not in s:
        balances=expect(200,http('GET',f"/api/inventory/tare/warehouses/{case.w}/balances"))
        balance=next(v for v in balances if v['pallet_type_id']==s['pallet_type_id']and v['custodian_kind']=='WAREHOUSE'and v['condition_code']=='GOOD')
        step('tare_count','/api/inventory/tare/count',dict(operation_id=case.tag+'.tare.count',owner_ware_id=case.w,pallet_type_id=s['pallet_type_id'],condition='GOOD',observed_quantity=str(int(balance['quantity'])+1),expected_version=balance['balance_version'],reason='Additional synthetic empty carton for isolated acceptance',decision_reference='TEST_FIXTURE_NOT_HARDWARE:'+case.tag))
    actor,password,_,_,_=case.start()
    if 'label_body'not in s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case']);carrier,version=q.fetchone()
        s['label_body']=dict(operation_id=case.tag+'.label',scan_container=carrier,expected_content_version=version);save()
    label=step('label',base+'/sscc-label',s['label_body'],actor=actor,password=password)
    step('confirmed',base+'/sscc-label/confirm',dict(scan=label['sscc']),actor=actor,password=password)
    s.setdefault('manual_body',dict(operation_id=case.tag+'.tare.manual',scan_container=label['sscc'],expected_content_version=label['content_version'],tare_weight_kg='0.1',measurement_ref='SYNTHETIC_MANUAL_NOT_HARDWARE:'+case.tag));save()
    return actor,password,base


def owner(key,view,operate):
    with oracle_connection()as c:
        q=c.cursor();q.execute("select VERSION_NO from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=:w and OWNER_ID='SNS'",a=s['actor'],w=case.w);version=q.fetchone()[0]
    return step(key,case.base+'/stock/owner-grants',dict(operation_id=case.tag+'.'+key,expected_version=version,username=s['actor'],owner_id='SNS',can_view=view,can_operate=operate,reason='Current owner authority on immutable manual tare replay'),'PUT')


def probes(actor,password,base):
    path=f"/api/inventory/warehouse-scales/tasks/{s['case']}/manual-empty-tare";body=s['manual_body']
    def own(method,url,value=None):return http(method,url,value,actor,password)
    if 'race'not in s:
        with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(lambda _:own('POST',path,body),range(2)))
        values=[expect(200,v)for v in responses];assert values[0]==values[1];s['race']=values;save()
    original=s['race'][0];assert expect(200,own('POST',path,body))==original
    changed=expect(409,own('POST',path,dict(body,tare_weight_kg='0.2')));assert changed['detail']['outcome_confirmed']is False
    for key,changes in [('stale',dict(expected_content_version=body['expected_content_version']+1)),('wrong-scan',dict(scan_container='OTHER_CARTON')),('zero',dict(tare_weight_kg='0'))]:
        value=expect(409,own('POST',path,dict(body,operation_id=case.tag+'.'+key,**changes)));s['checks'].append(dict(test=key,result=value));save()
    expect(403,own('POST','/api/inventory/warehouse-scales/tasks/1159/manual-empty-tare',body))
    label=expect(200,own('POST',base+'/sscc-label',s['label_body']));assert label==s['label']
    expect(409,own('POST',base+'/sscc-label',dict(s['label_body'],scan_container='OTHER_CARTON')))
    if 'owner-restored'not in s:
        owner('owner-revoked',False,False)
        assert expect(403,own('POST',path,body))['detail']['outcome_confirmed']is False
        expect(403,own('POST',base+'/sscc-label',s['label_body']))
        owner('owner-restored',True,True)
    assert expect(200,own('POST',path,body))==original
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a and REVOKED_AT is null',a=actor);assert q.rowcount==1;c.commit()
    try:
        assert expect(403,own('POST',path,body))['detail']['outcome_confirmed']is False
        expect(403,own('POST',base+'/sscc-label',s['label_body']))
    finally:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=null where ASSIGNMENT_ID=:a',a=actor);c.commit()
    assert expect(200,own('POST',path,body))==original
    assert expect(200,own('POST',base+'/sscc-label',s['label_body']))==label
    step('remeasured',path,dict(body,operation_id=case.tag+'.remeasured',tare_weight_kg='0.2'),actor=actor,password=password)
    current=expect(200,own('GET',base+'/sscc-label'));assert current['manual_empty_tare']['tare_weight_kg']=='0.2'
    with oracle_connection()as c:
        q=c.cursor();q.execute('select count(*)from RRL_CASE_MANUAL_TARE where CASE_PICK_TASK_ID=:t',t=s['case']);assert q.fetchone()[0]==2
        q.execute('select RRL_HAS_WRIGHT(:a,\'case_pick_execute\')from dual',a=actor);assert q.fetchone()[0]==0
    s['checks'].append('same-op race/replay/conflict/foreign/stale/scan/zero/owner/assignment/label/remeasure');save()


def cleanup(base):
    step('cancelled',base+'/return-carrier',dict(operation_id=case.tag+'.cancel',scan_container=s['label']['sscc'],expected_content_version=s['label']['content_version'],destinations={},allow_empty=True,reason='Cancel empty manual-tare verification without picking goods'))
    step('logout',f"/api/resources/sessions/{s['session']['id']}/logout",dict(reason='Manual tare replay acceptance complete'))
    owner('retired-owner',False,False)
    step('qualification-off',f"/api/resources/{s['resource']['id']}/qualifications",dict(task_type='CASE_PICK',active=False),'PUT')
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=s['actor']);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=s['actor']);c.commit()
        q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=case.w);s['stock_after']=list(q.fetchone())
    s['qa_retired']=True;save()


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        if s.get('status')!='PASS':
            actor,password,base=prepare();probes(actor,password,base);cleanup(base);s['status']='PASS';save()
        print(json.dumps(dict(status=s['status'],case=s['case'],stock=s['stock_after'],qa_retired=s['qa_retired'])))
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
