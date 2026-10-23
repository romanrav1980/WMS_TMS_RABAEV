"""Independent read/metadata-guard verification of the completed owned inbound yard fixture."""
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb
import requests

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T10'
source=json.loads((OUT/'YI2338ff7c3a0f.json').read_text(encoding='utf-8'))
tag=source['tag'];report=dict(status='FAIL',checks=[])
try:
    with oracle_connection()as c:
        q=c.cursor()
        for sql in ["update RRL_YARD_VISIT_SUPPLY set DOCUMENT_VERSION=DOCUMENT_VERSION where VISIT_ID=408 and SUPPLY_ID=:s",
                    "insert into RRL_YARD_VISIT_SUPPLY(VISIT_ID,WARE_ID,SUPPLY_ID,DOCUMENT_VERSION)values(408,220793322,:s,1)"]:
            q.execute('savepoint inbound_guard')
            try:
                q.execute(sql,s=tag+'.A1'if sql.startswith('update')else tag+'.UNTRUSTED')
                raise AssertionError('Untrusted supply link mutation accepted')
            except oracledb.DatabaseError as error:
                assert 'YARD_SUPPLY_LINK_IMMUTABLE'in str(error),str(error)
            finally:q.execute('rollback to inbound_guard')
        c.rollback()
        report['checks'].append('Direct insert and update of supply links denied by native guard')
        q.execute('select v.VISIT_ID,v.STATE from RRL_YARD_VISIT v where exists(select 1 from RRL_YARD_VISIT_EVENT e where e.VISIT_ID=v.VISIT_ID and e.OPERATION_ID like :tag)order by v.VISIT_ID',tag=tag+'%')
        visits=list(q);assert visits and all(s in ('CANCELLED','DEPARTED')for _,s in visits);report['visits']=visits
        q.execute("select count(*)from RUSERS where ID=:a and nvl(DELETED,0)=0",a=tag+'.QA');assert q.fetchone()==(0,)
        q.execute("select CAN_VIEW,CAN_OPERATE from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=220793322 and OWNER_ID='SNS'",a=tag+'.QA');assert q.fetchone()==(0,0)
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
        q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID')
        report['stock']=[list(r)for r in q];assert report['stock']==source['stock']
        report['checks'].append('All own visits closed, actor retired, owner access zero, original stocks preserved, INVALID0')
    start=time.perf_counter()
    response=requests.get('http://127.0.0.1:8088/api/resources/timeline',params=dict(warehouse_id=220793322,start_at='2026-10-22T23:00:00Z',finish_at='2026-10-24T00:00:00Z'),auth=('admin','admin123'),timeout=30)
    report['timeline_ms']=round((time.perf_counter()-start)*1000,2)
    assert response.status_code==200,(response.status_code,response.text[:500])
    payload=response.json();events=[e for e in payload['events']if e['event_id']in ('YARD_VISIT:408','YARD_VISIT:410')]
    assert len(events)==2 and all('приёмка'in e['label']and e['fact_finish_at']for e in events),events
    report['timeline_events']=events
    report['checks'].append('Real resource timeline contains both completed inbound vehicle intervals with the receiving label')
    report['status']='PASS'
finally:
    (OUT/'inbound-independent-verification.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']))))
