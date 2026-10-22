"""Select an actual carton while CASE is empty, then pick through the original flow."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import live_factory_case as case
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07';FILE=OUT/'bulk-small-case.json'
f=json.loads((OUT/'bulk-source-state.json').read_text(encoding='utf-8'))['fixture'];w=f['warehouse_id']
old=json.loads((OUT/'bulk-case-0.json').read_text(encoding='utf-8'))
case.OUT=OUT;case.FILE=FILE;case.w=w;case.base=f'/api/tradecase/warehouses/{w}';case.tag='BS22.'+str(w)
case.s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(warehouse_id=w,article=f['article'],pick=f['pick'],face=old['face'],cpt_policy=old['cpt_policy'],history=[])


def prepare():
    case.prepare()
    code='BULK22.CARTON.'+str(w)
    if 'pallet_type_id'not in case.s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select PALLET_TYPE_ID,LOAD_UNIT_CLASS,DEFAULT_WEIGHT_KG,FINAL_WEIGHT_REQUIRED from RRL_PALLET_TYPE where PALLET_TYPE_CODE=:code',code=code);row=q.fetchone()
        if row:
            assert row[1:] == ('CONTAINER',0.1,1);type_id=row[0]
        else:
            type_id=expect(200,http('POST','/api/case-pick/pallet-types',dict(pallet_type_code=code,pallet_type_name='TRADECASE test carton',load_unit_class='CONTAINER',default_volume_m3='0.1',default_weight_kg='0.1',length_mm='400',width_mm='500',height_mm='500',expected_version=0,final_weight_required=True,active=1)))['pallet_type_id']
        case.s['pallet_type_id']=type_id;case.save()
    if 'small_type_body'not in case.s:
        current=expect(200,http('GET',f"/api/case-pick/tasks/{case.s['case']}/pallet-type"))
        assert current['can_change_empty_type']
        case.s['small_type_body']=dict(operation_id=case.tag+'.type',pallet_type_id=case.s['pallet_type_id'],expected_version=current['version'],scan_container=current['sscc'],reason='Choose actual carton before the first physical pick');case.save()
    case.step('small_type_set',f"/api/case-pick/tasks/{case.s['case']}/pallet-type",case.s['small_type_body'])
    with oracle_connection()as c:
        q=c.cursor();q.execute('select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=case.s['case']);assert q.fetchone()[0]==case.s['pallet_type_id']


def pick():
    assert 'small_type_set'in case.s
    if 'small_label_body'not in case.s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=case.s['case']);sscc,version=q.fetchone()
        case.s['small_label_body']=dict(operation_id=case.tag+'.label',scan_container=sscc,expected_content_version=version);case.save()
    with oracle_connection()as c:
        q=c.cursor();q.execute('select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0',a=case.s['actor']);row=q.fetchone();assert row,'Do not reactivate a retired QA actor';password=row[0]
    path=f"/api/case-pick/tasks/{case.s['case']}/sscc-label"
    label=case.step('small_label',path,case.s['small_label_body'],actor=case.s['actor'],password=password)
    case.step('small_label_confirm',path+'/confirm',dict(scan=label['sscc']),actor=case.s['actor'],password=password)
    if 'rejected_pick_body'not in case.s and 'pick_body'in case.s:
        with oracle_connection()as c:
            q=c.cursor();q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=case.s['pick_body']['operation_id']);assert q.fetchone()[0]==0
        case.s['rejected_pick_body']=case.s['pick_body']
        case.s['pick_body']=dict(case.s['pick_body'],operation_id=case.tag+'.pick.labeled',scan_container=label['sscc']);case.save()
    if 'manual_tare_body'not in case.s:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=case.s['case']);carrier,version=q.fetchone()
        case.s['manual_tare_body']=dict(operation_id=case.tag+'.manual.tare',expected_content_version=version,scan_container=carrier,tare_weight_kg='0.1',measurement_ref='SYNTHETIC_MANUAL_NOT_HARDWARE:'+case.tag);case.save()
    tare=case.step('manual_tare',f"/api/inventory/warehouse-scales/tasks/{case.s['case']}/manual-empty-tare",case.s['manual_tare_body'],actor=case.s['actor'],password=password)
    assert tare['origin']=='MANUAL_CONFIRMED'and tare['stock_changed']is False
    if not case.s.get('small_closed'):case.execute(return_after=False);case.s['small_closed']=True;case.save()
    if not case.s.get('small_picker_retired'):
        actor=case.s['actor']
        case.step('small_logout',f"/api/resources/sessions/{case.s['session']['id']}/logout",dict(reason='Actual carton CASE picking complete'))
        case.step('small_revoke_owner',case.base+'/stock/owner-grants',dict(operation_id=case.tag+'.retire',expected_version=1,username=actor,owner_id='SNS',can_view=False,can_operate=False,reason='Retire actual carton picking QA'),'PUT')
        case.step('small_qualification_off',f"/api/resources/{case.s['resource']['id']}/qualifications",dict(task_type='CASE_PICK',active=False),'PUT')
        with oracle_connection()as c:
            q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        case.s['small_picker_retired']=True;case.save()
    print(json.dumps(dict(case_id=case.s['case'],pallet_type_id=case.s['pallet_type_id'],status='SMALL_CASE_PICKED_QA_RETIRED')))


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:pick()if '--pick'in sys.argv else prepare()
    except Exception as exc:case.s['error']=str(exc);case.save();raise
    finally:case.s['history']+=CALLS;case.save()
