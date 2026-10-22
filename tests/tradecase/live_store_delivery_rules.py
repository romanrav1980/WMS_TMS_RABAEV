"""Delivery-rule edits preserve old requests and reject concurrent legacy changes."""
import json
from pathlib import Path
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT),str(ROOT/'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,CALLS

TAG='DR23'+uuid4().hex[:10]
ADDR=TAG+'.STORE'
PATH='/api/master-data/stores/profile'
report=dict(status='FAIL',fixture='Own synthetic address; actual profile API and Oracle address/window state',http=CALLS)


def call(method,path,body=None,status=200):
    code,result=http(method,path,body,'admin','admin123')
    assert code==status,(code,result)
    return result


def stock(q):
    q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID')
    return [list(r)for r in q]


if __name__=='__main__':
    created=False
    try:
        with oracle_connection() as c:
            q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
            before=stock(q)
            q.execute('insert into RRL_ADDR(ADDR,SHIROTA,DOLGOTA,DELETED3)values(:a,55.75,37.61,0)',a=ADDR)
            q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
            c.commit();created=True
        initial=call('GET',PATH+'?addr='+ADDR)
        assert initial['version']==0
        body=dict(operation_id=TAG+'.save',store_addr=ADDR,expected_version=0,reason='Owned delivery rule acceptance',
                  receiving_window_mode='WEEKLY',timezone_region='UTC',windows=[dict(weekday=5,from_minute=660,to_minute=720)],
                  unload_norm_min=30,window_strict=True,expected_delivery_rules_hash=initial['delivery_rules']['source_hash'])
        saved=call('PUT',PATH,body)
        assert saved['delivery_rules']['unload_norm_min']==30 and saved['delivery_rules']['window_strict'] is True
        assert call('PUT',PATH,body)==saved
        # An unchanged old client request carries no new rule fields; preserve its hash and current rules.
        legacy={k:v for k,v in body.items()if k not in('unload_norm_min','window_strict','expected_delivery_rules_hash')}
        legacy.update(operation_id=TAG+'.legacy',expected_version=1,access_note='Legacy request compatibility')
        legacy_saved=call('PUT',PATH,legacy)
        assert call('PUT',PATH,legacy)==legacy_saved
        assert legacy_saved['delivery_rules']['unload_norm_min']==30 and legacy_saved['windows']==saved['windows']
        with oracle_connection() as c:
            # Deliberate owned legacy-writer simulation: no profile version change.
            q=c.cursor();q.execute('update RRL_ADDR set UNLOAD_NORM_MIN=45 where ADDR=:a',a=ADDR);assert q.rowcount==1;c.commit()
        stale=dict(body,operation_id=TAG+'.stale',expected_version=2,unload_norm_min=60,
                   expected_delivery_rules_hash=saved['delivery_rules']['source_hash'])
        refused=call('PUT',PATH,stale,status=409)
        assert refused['detail']['code']=='STORE_DELIVERY_RULES_CHANGED'
        current=call('GET',PATH+'?addr='+ADDR)
        assert current['version']==2 and current['delivery_rules']['unload_norm_min']==45 and current['windows']==saved['windows']
        soft=dict(legacy,operation_id=TAG+'.soft',expected_version=2,window_strict=False,
                  expected_delivery_rules_hash=current['delivery_rules']['source_hash'])
        result=call('PUT',PATH,soft)
        assert result['delivery_rules']['window_strict'] is False and result['delivery_rules']['unload_norm_min']==45
        report['checks']=['Norm/strictness/weekly window saved and exact replayed',
                          'Old unchanged request replayed, norm and windows retained',
                          'Concurrent legacy norm change rejects stale edit without publishing profile',
                          'Fresh partial strictness edit preserves duration and windows']
        with oracle_connection() as c:
            q=c.cursor();q.execute('select UNLOAD_NORM_MIN,TW_STRICT from RRL_ADDR where ADDR=:a',a=ADDR);assert q.fetchone()==(45,0)
            q.execute('select count(*)from RRL_STORE_PROFILE_CHANGE where OPERATION_ID=:op',op=TAG+'.stale');assert q.fetchone()==(0,)
        report['status']='PASS'
    finally:
        if created:
            with oracle_connection() as c:
                q=c.cursor();q.execute('update RRL_ADDR set DELETED3=1 where ADDR=:a',a=ADDR);c.commit()
                assert stock(q)==before;report['stock']=before
                q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
                q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only',m=marker)
                report['slow_sql']=[list(r)for r in q]
            report['fixture_retired']=True
        out=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T09'/(TAG+'.json')
        out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(out))))
