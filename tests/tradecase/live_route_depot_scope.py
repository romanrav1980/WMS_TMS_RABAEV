"""Actual HTTP/native depot save, replay and revoked warehouse assignment."""
import hashlib
import json
from pathlib import Path
import secrets
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT),str(ROOT/'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,CALLS

TAG='RS23'+uuid4().hex[:10]
WARE=240000000+secrets.randbelow(9000000)
ADDRESS=TAG+'.DEPOT'
PASSWORD=secrets.token_hex(24)
report=dict(status='FAIL',warehouse=WARE,fixture='Synthetic warehouse/address, actual HTTP/native depot commands',http=CALLS)
created=False
version=0


def call(method,path,body=None,actor='admin',status=200):
    code,result=http(method,path,body,actor,PASSWORD if actor==TAG else 'admin123')
    assert code==status,(code,result)
    return result


if __name__=='__main__':
    try:
        with oracle_connection() as c:
            q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
            q.execute('insert into RRL_WARES(ID,NAME)values(:w,:n)',w=WARE,n='TRADECASE QA route '+TAG)
            q.execute('insert into RRL_ADDR(ADDR,SHIROTA,DOLGOTA,DELETED3)values(:a,55.75,37.61,0)',a=ADDRESS)
            q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'Route settings QA',1,1)",w=str(WARE))
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Route settings QA','TC03QA',:w,0,1)",a=TAG,p=PASSWORD,w=WARE)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Route settings QA',1,1)",a=TAG)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'warehouse_settings_edit')",a=TAG)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Route settings acceptance',1)",a=TAG,w=str(WARE))
            q.execute("select RRL_HAS_WRIGHT(:a,'warehouse_settings_edit')from dual",a=TAG);assert q.fetchone()==(0,)
            q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
            c.commit();created=True
        path='/api/transport/warehouse-depots'
        assert call('GET',path+'/'+str(WARE),actor=TAG)['version']==0
        body=dict(operation_id=TAG+'.save',warehouse_id=WARE,expected_version=0,depot_address=ADDRESS,reason='Synthetic route settings acceptance')
        result=call('POST',path,body,TAG);version=result['version'];assert version==1 and result['operation_id']==body['operation_id']
        assert call('POST',path,body,TAG)==result
        call('POST',path,dict(body,reason='Changed request acceptance'),TAG,409)
        call('POST',path,dict(body,operation_id=TAG+'.stale'),TAG,409)
        call('GET',path+'/220793322',actor=TAG,status=403)
        resolved=call('POST',path+'/resolve',body,TAG)
        assert resolved['state']=='RECORDED' and resolved['result']==result
        with oracle_connection() as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=TAG);c.commit()
        call('POST',path,body,TAG,403)
        call('POST',path+'/resolve',body,TAG,403)
        report['checks']=['Role-only own save/replay/resolve','Changed body and stale version denied','Foreign warehouse and revoked replay/resolve denied']
        report['status']='PASS'
    finally:
        if created:
            call('POST','/api/transport/warehouse-depots',dict(operation_id=TAG+'.clear',warehouse_id=WARE,expected_version=version,depot_address=None,reason='Clear synthetic acceptance setting'))
            with oracle_connection() as c:
                q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG)
                q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=TAG)
                q.execute('update RRL_ADDR set DELETED3=1 where ADDR=:a',a=ADDRESS);c.commit()
                q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
                q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only',m=marker)
                report['slow_sql']=[list(r)for r in q]
            report['qa_retired']=True
        out=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T09'/(TAG+'.json')
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(out))))
