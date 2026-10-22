"""Native current-owner checks on immutable HU receipts; no physical posting."""
import json,os,secrets,sys
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07';FILE=OUT/'bulk-wait-owner-replay.json'
s=json.loads(FILE.read_text())if FILE.exists()else dict(checks=[],history=[])


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def probe(q,op,denied):
    q.execute('select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=op);raw=q.fetchone()[0]
    request=json.dumps(raw)if isinstance(raw,dict)else raw.read()if hasattr(raw,'read')else raw
    try:q.callproc('RRL_HU_EXEC_ACCESS.assert_request',[request,s['actor']])
    except Exception as exc:
        assert denied and getattr(exc.args[0],'code',None)==20882,str(exc);s['checks'].append(dict(operation=op,result='DENIED',reason=str(exc).split('\n')[0]));save();return
    assert not denied,'Current owner access was bypassed';s['checks'].append(dict(operation=op,result='ALLOWED'));save()


def grant(view,operate):
    with oracle_connection()as c:
        q=c.cursor();q.execute("select VERSION_NO from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=220793322 and OWNER_ID='SNS'",a=s['actor']);row=q.fetchone();version=row[0]if row else 0
    result=expect(200,http('PUT','/api/tradecase/warehouses/220793322/stock/owner-grants',dict(operation_id=s['actor']+'.owner.'+str(version),expected_version=version,username=s['actor'],owner_id='SNS',can_view=view,can_operate=operate,reason='Native immutable HU current-owner acceptance')));s['owner_version']=result['version'];save()


def run():
    before='--before'in sys.argv
    with oracle_connection()as c:
        q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
        if 'actor'not in s:
            name='WR22'+uuid4().hex[:10]
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'HU owner replay QA',:a,220793322,0,1)",a=name,p=secrets.token_hex(24))
            q.execute("insert into USER_GROUP(ID,NAME)values(:a,'HU owner replay QA')",a=name)
            for right in ['warehouse_task_edit','warehouse_task_execute']:q.execute('insert into RIGHTS(RIGHT1,USER_GROUP)values(:r,:a)',r=right,a=name)
            c.commit();s['actor']=name;save()
        q.execute("select DELETED,RRL_HAS_WRIGHT(ID,'warehouse_task_execute')from RUSERS where ID=:a",a=s['actor']);assert q.fetchone()==(0,1),'Do not reactivate retired QA'
        for op in ['NB22.WAIT.PLAN.B','NB22.WAIT.COMPLETE.B']:probe(q,op,not before)
    if before:s['baseline']='OWNERLESS_LEGACY_EXECUTOR_WAS_ALLOWED';save();return
    grant(True,False)
    with oracle_connection()as c:
        for op in ['NB22.WAIT.PLAN.B','NB22.WAIT.COMPLETE.B']:probe(c.cursor(),op,True)
    grant(True,True)
    with oracle_connection()as c:
        for op in ['NB22.WAIT.PLAN.B','NB22.WAIT.COMPLETE.B']:probe(c.cursor(),op,False)
    grant(False,False)
    with oracle_connection()as c:
        q=c.cursor()
        for op in ['NB22.WAIT.PLAN.B','NB22.WAIT.COMPLETE.B']:probe(q,op,True)
        q.execute('update RUSERS set DELETED=1 where ID=:a and USER_GROUP=:a',a=s['actor']);q.execute('delete from RIGHTS where USER_GROUP=:a',a=s['actor']);c.commit()
    s.update(status='PASS',qa_retired=True,limitation='Pure native admission probes; they do not impersonate the original operation actor or post its command.');save()
    print(json.dumps(dict(status=s['status'],checks=len(s['checks']),qa_retired=True)))


if __name__=='__main__':
    try:run()
    finally:s['history']+=CALLS;save()
