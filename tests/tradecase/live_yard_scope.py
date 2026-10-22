"""Real HTTP/Oracle owner, actor-bound replay and revocation for one owned yard visit."""
import hashlib
import json
import secrets
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts'), str(ROOT/'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http, CALLS

W=220793322
TAG='YS22'+uuid4().hex[:10]
PASSWORD=secrets.token_hex(24)
BASE=f'/api/tradecase/warehouses/{W}'
report=dict(status='FAIL', fixture='Synthetic source documents; real HTTP/Oracle, no physical arrival', checks=[], http=CALLS)
version=0
visit=None


def call(method,path,body=None,actor='admin',status=200):
    code,result=http(method,path,body,actor,PASSWORD if actor==TAG else 'admin123')
    assert code in (status if isinstance(status, tuple) else (status,)),(code,result)
    return result


def grant(view,operate):
    global version
    result=call('PUT',BASE+'/stock/owner-grants',dict(operation_id=TAG+'.grant.'+str(version),expected_version=version,
        username=TAG,owner_id='SNS',can_view=view,can_operate=operate,reason='Owned yard scope acceptance'))
    version=result['version']


if __name__=='__main__':
    created=False
    try:
        with oracle_connection() as c:
            q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
            q.execute('select NAME from RRL_WARES where ID=:w',w=W);assert q.fetchone()[0].startswith('TRADECASE QA ')
            for entity,body in [('ORDER',dict(lines=[dict(line_id='1',source_owner_id='SNS')])),('TRIP',dict(orders=[dict(order_id=TAG+'.ORDER',line_id='1')]))]:
                raw=json.dumps(body)
                q.execute("insert into RRL_TRADE_DOCUMENT(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)values(:w,:e,:id,'TC03.SAP',1,:h,:body,'ACCEPTED','admin')",w=W,e=entity,id=TAG+'.'+entity,h=hashlib.sha256(raw.encode()).hexdigest(),body=raw)
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Owned yard QA','TC03QA',:w,0,1)",a=TAG,p=PASSWORD,w=W)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Owned yard QA',1,1)",a=TAG)
            for permission in ('tradecase_view','tradecase_yard_operate'):
                q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=TAG,p=permission)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Owned yard QA',1)",a=TAG,w=str(W))
            c.commit();created=True
        path=BASE+'/yard/visits'
        body=dict(operation_id=TAG+'.expect',trip_id=TAG+'.TRIP')
        call('POST',path,body,TAG,409)
        grant(True,False)
        call('POST',path,body,TAG,403)
        grant(True,True)
        receipt=call('POST',path,body,TAG)
        visit=receipt['visit_id']
        assert receipt['operation_id']==body['operation_id']
        assert call('POST',path,body,TAG)['replayed'] is True
        call('POST',path,body,'admin',409)
        call('POST',path,dict(body,trip_id=TAG+'.OTHER'),TAG,409)
        assert any(v['visit_id']==visit for v in call('GET',path,actor=TAG)['visits'])
        report['checks'].append('Unbound ORDER owner denies absent/read-only grants; operate succeeds, same actor replays, other actor/body conflict')
        grant(False,False)
        assert all(v['visit_id']!=visit for v in call('GET',path,actor=TAG)['visits'])
        call('POST',path,body,TAG,409)
        grant(True,True)
        with oracle_connection() as c:
            q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG);c.commit()
        call('POST',path,body,TAG,(401,403))
        call('GET',path,actor=TAG,status=(401,403))
        report['checks'].append('Owner revocation hides existing visit and receipt; retired user denied')
        report['status']='PASS'
    finally:
        if created:
            if visit:
                call('POST',BASE+f'/yard/visits/{visit}/transitions',dict(operation_id=TAG+'.cleanup',expected_version=1,action='CANCEL',reason='Owned acceptance completed'))
            # Grant API correctly refuses an already retired user. Reactivate only this
            # freshly created QA to revoke its own grant, then retire it again.
            with oracle_connection() as c:
                q=c.cursor();q.execute('update RUSERS set DELETED=0 where ID=:a',a=TAG);c.commit()
            grant(False,False)
            with oracle_connection() as c:
                q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG)
                q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=TAG)
                c.commit()
                q.execute('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=W)
                assert q.fetchone()==(7,5)
            report['qa_retired']=True
        out=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T10'/(TAG+'.json')
        out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(out))))
