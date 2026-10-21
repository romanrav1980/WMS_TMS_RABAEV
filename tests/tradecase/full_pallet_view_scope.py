"""Current warehouse and owner visibility on the real bound full-pallet movement."""
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
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06';actor='FPV21'+uuid4().hex[:9];password=secrets.token_hex(24)
WARE=221164919;path='/api/warehouse-tasks/1219/full-pallet-shipment';report=dict(status='FAIL',checks=[])


def run():
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        q.execute('select NAME from RRL_WARES where ID=:w',w=WARE);assert q.fetchone()==('TRADECASE QA aa5cf70d',)
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Full pallet viewer QA','TC03QA',:w,0,1)",a=actor,p=password,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Full pallet viewer QA',1,1)",a=actor)
        q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'warehouse_task_view')",a=actor)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Full pallet current owner view',1)",a=actor,w=str(WARE));c.commit()
    def own():return http('GET',path,actor=actor,password=password)
    expect(409,own());report['checks'].append('warehouse role alone does not expose owner stock')
    grant=dict(operation_id=actor+'.grant',expected_version=0,username=actor,owner_id='SNS',can_view=True,can_operate=False,reason='Full pallet view scope test')
    url=f'/api/tradecase/warehouses/{WARE}/stock/owner-grants'
    expect(200,http('PUT',url,grant));r=expect(200,own());assert r['quantity']=='10'and r['pallet_identifier']=='690000000582192776'
    report['checks'].append('current warehouse+SNS view exposes actual ten pieces')
    expect(200,http('PUT',url,dict(grant,operation_id=actor+'.revoke',expected_version=1,can_view=False)))
    expect(409,own());report['checks'].append('owner revoke hides prior preview')
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
    expect(409,own());report['checks'].append('warehouse role revoke hides preview')
    report['status']='PASS'


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:run()
    except Exception as exc:report['error']=str(exc);raise
    finally:
        with oracle_connection()as c:
            q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        report['actor']=actor;report['history']=CALLS;(OUT/('fullpal-scope-'+actor+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],actor=actor,checks=report['checks'])))
