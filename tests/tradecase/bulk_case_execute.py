"""Execute two scoped CASE sessions on the retained bulk fixture; keep picked boxes."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
import live_factory_case as case
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07'
FILE=OUT/'bulk-execution.json'
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(status='IN_PROGRESS',warehouse=220793322,history=[])


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def configure(i):
    case.OUT=OUT;case.FILE=OUT/f'bulk-case-{i}.json';case.s=json.loads(case.FILE.read_text(encoding='utf-8'))
    case.w=s['warehouse'];case.base=f"/api/tradecase/warehouses/{case.w}";case.tag=f'BULK22.{i}.{case.w}'


def retire():
    for i in range(2):
        configure(i);actor=case.s['actor']
        case.step('bulk_logout',f"/api/resources/sessions/{case.s['session']['id']}/logout",dict(reason='Bulk box CASE picking complete'))
        case.step('bulk_revoke_owner',case.base+'/stock/owner-grants',dict(operation_id=case.tag+'.bulk.retire',expected_version=1,username=actor,owner_id='SNS',can_view=False,can_operate=False,reason='Retire isolated bulk CASE owner access'),'PUT')
        case.step('bulk_qualification_off',f"/api/resources/{case.s['resource']['id']}/qualifications",dict(task_type='CASE_PICK',active=False),'PUT')
        with oracle_connection()as c:
            q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
    s['qa_retired']=True;save()


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        if 'tare'not in s:
            s['tare']=expect(200,http('POST','/api/inventory/tare/count',dict(operation_id='BULK22.TARE.COUNT',owner_ware_id=s['warehouse'],pallet_type_id=1,condition='GOOD',observed_quantity='2',expected_version=0,
                reason='Synthetic isolated bulk fixture, not physical tare survey',decision_reference='TEST_FIXTURE_NOT_HARDWARE:BULK22')));save()
        for i in range(2):
            configure(i)
            if case.s.get('bulk_picking_complete'):continue
            case.s['tare_count']=s['tare']
            if i:case.s['cpt_policy']=json.loads((OUT/'bulk-case-0.json').read_text(encoding='utf-8'))['cpt_policy']
            case.save();case.execute(return_after=False);case.s['bulk_picking_complete']=True;case.save()
        retire()
        with oracle_connection()as c:
            q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse']);s['stock']=list(q.fetchone());assert s['stock']==[10,4]
            q.execute("select CASE_PICK_TASK_ID,STATUS,SSCC,CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(1161,1162)order by CASE_PICK_TASK_ID");s['cases']=[list(x)for x in q]
        s['status']='PICKED_CASES_QA_RETIRED';save();print(json.dumps(dict(status=s['status'],stock=s['stock'],cases=s['cases'])))
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
