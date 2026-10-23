"""Owned role/owner/window admission for wave-specific CASE reads; no goods writes."""
import json,os,secrets,sys
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T10';OUT.mkdir(exist_ok=True)
s=dict(checks=[],status='FAIL');actor=None


def run():
    global actor
    with oracle_connection()as c:
        q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
        actor='WF22'+uuid4().hex[:10];password=secrets.token_hex(24)
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Wave filter QA','TC03QA',222823304,0,1)",a=actor,p=password)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Wave filter QA',1,1)",a=actor)
        for permission in ['case_pick_view','resource_gantt_view','transport_dispatch_view','tradecase_view']:
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)",a=actor,p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE','220793322','CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Bounded selected-wave native admission',1)",a=actor);c.commit()
        q.execute("select RRL_HAS_WRIGHT(:a,'case_pick_view'),RRL_ACCESS_API.allowed(:a,'case_pick_view','WAREHOUSE','220793322')from dual",a=actor);assert q.fetchone()==(0,1)
    s['actor']=actor
    path='/api/case-pick/tasks?scope=all&ware_id=220793322&include_closed=true&limit=1&pick_wave_id=613'
    def own(url=path):return http('GET',url,actor=actor,password=password)
    timeline='/api/resources/timeline?warehouse_id=220793322&start_at=2026-10-22T00:00:00%2B03:00&finish_at=2026-10-23T00:00:00%2B03:00'
    coverage='/api/tradecase/warehouses/220793322/trips/R1.1168/coverage'
    def points():return [e for e in expect(200,own(timeline))['events']if e['kind']in('LOAD_CONFIRMATION','TRIP_DEPARTURE')]
    assert expect(200,own())==[];s['checks'].append('No owner grant hides before limit')
    assert points()==[];s['checks'].append('No owner grant hides frozen loading facts')
    hidden=expect(200,own(coverage));assert hidden['lines']==[] and hidden['unattributed_loads'] is None;s['checks'].append('No owner grant hides coverage without exposing counts')
    def grant(version,view):return expect(200,http('PUT','/api/tradecase/warehouses/220793322/stock/owner-grants',dict(operation_id=actor+'.owner.'+str(version),expected_version=version,username=actor,owner_id='SNS',can_view=view,can_operate=False,reason='Read-only wave-specific visibility acceptance')))
    grant(0,True)
    rows=expect(200,own());assert [r['case_pick_task_id']for r in rows]==[1169];s['checks'].append('Scoped role and owner view select wave before limit')
    assert 'LOAD_CONFIRMATION:NB22.LOAD.A'in {e['event_id']for e in points()};s['checks'].append('Owner view reveals frozen loading fact and aware milestone')
    visible=expect(200,own(coverage));assert visible['lines'][0]['departed_base']=='1' and visible['load_coverage_complete'];s['checks'].append('Owner view reveals real departed coverage')
    assert [r['case_pick_task_id']for r in expect(200,own(path.replace('613','612')))]==[1168];s['checks'].append('Independent wave cannot reuse selected rows')
    expect(403,own(path.replace('613','604')));s['checks'].append('Foreign wave cannot borrow selected warehouse')
    expect(403,own(path.replace('220793322','221164919').replace('613','604')));s['checks'].append('Foreign warehouse denied')
    expect(404,own(path.replace('613','999999999')));expect(422,own(path.replace('613','0')))
    grant(1,False);assert expect(200,own())==[];s['checks'].append('Owner revoke hides without goods effects')
    assert points()==[];s['checks'].append('Owner revoke hides already issued frozen loading facts')
    assert expect(200,own(coverage))['lines']==[];s['checks'].append('Owner revoke hides coverage after departure')
    grant(2,True)
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
    expect(403,own());s['checks'].append('Warehouse role revoke denies selected wave')
    expect(403,own(timeline));s['checks'].append('Warehouse role revoke denies timeline')
    expect(403,own(coverage));s['checks'].append('Warehouse role revoke denies coverage')
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=220793322');s['stock']=list(q.fetchone());assert s['stock']==[7,5]
        q.execute("select count(*)from user_objects where STATUS='INVALID'");assert q.fetchone()[0]==0
    s['status']='PASS'


if __name__=='__main__':
    try:run()
    finally:
        if actor:
            with oracle_connection()as c:
                q=c.cursor();q.execute("select VERSION_NO from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=220793322 and OWNER_ID='SNS'",a=actor);row=q.fetchone()
            if row:expect(200,http('PUT','/api/tradecase/warehouses/220793322/stock/owner-grants',dict(operation_id=actor+'.retire',expected_version=row[0],username=actor,owner_id='SNS',can_view=False,can_operate=False,reason='Retire isolated wave read acceptance')))
            with oracle_connection()as c:
                q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
            s['qa_retired']=True
        s['history']=CALLS;(OUT/'wave-case-filter.json').write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
    print(json.dumps({k:v for k,v in s.items()if k!='history'}))
