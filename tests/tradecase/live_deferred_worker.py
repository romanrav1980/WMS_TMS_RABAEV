"""Live bounded deferred-worker proof on a fresh metadata-only warehouse."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from time import perf_counter
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER','admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD','admin123')
import live_document_acceptance as base
from tools.mcp.tms_mcp_server import oracle_connection
from api.wms_api_server.app.oracle_gateway import OracleGateway
from api.wms_api_server.app.transaction_gateway import TransactionGateway
from api.wms_api_server.app.modules.integrations.infrastructure.trade_deferred_worker import TradeDeferredWorker
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T02'


def run(f, report):
    ware,actor,password=f['warehouse_id'],f['actor'],f['password']
    path=f'/api/tradecase/warehouses/{ware}'
    checks=report['checks']
    def send(key,payload):
        body=dict(schema_version=1,event_id=uuid4().hex,source_id='SAP_QA',warehouse_id=ware,
                  document_id=key,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=payload)
        answer=base.expect(200,base.http('POST','/api/tradecase/messages',body,actor,password))
        return body,answer
    def sql(statement,**binds):
        with oracle_connection() as conn:
            cur=conn.cursor();cur.execute(statement,binds);return cur.fetchall()
    def work(service=None,limit=25):
        began=perf_counter();value=(service or TradeDeferredWorker(OracleGateway())).reconcile(ware,actor,limit)
        report['batches'].append(dict(elapsed_ms=round((perf_counter()-began)*1000,2),result=value))
        return value
    base.expect(200,base.http('PUT',path+'/site',dict(operation_id='setup',expected_version=0,source_id='SAP_QA',active_skm='SAP_QA',planning_source='SAP',enabled=True,reason='Deferred worker isolated acceptance')))
    for owner in ('SNS','BLC'): send(owner,dict(entity_type='OWNER',title=owner))
    send('C',dict(entity_type='RECIPIENT',title='Recipient',target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',lead_time_days=1,min_osg_days=0))
    line=dict(line_id='10',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='1',uom='BOX',min_osg_days=0)
    order=dict(entity_type='ORDER',recipient_id='C',planned_ship_at='2026-10-23T12:00:00+03:00',lines=[line])
    first=[]
    for key in ('O1','O2'):
        body,answer=send(key,order);assert answer['status']=='WAITING';first.append(body)
    assert work(limit=1)['waiting']==1
    checks.append('Bounded batch retries only one waiting message')
    send('A',dict(entity_type='SKU',title='Article A',units_per_box=10,permitted_mrc=['200']))
    with oracle_connection() as conn:
        cur=conn.cursor();cur.execute('select WARE_ID from RRL_TRADE_SITE where WARE_ID=:w for update',w=ware)
        assert work()['status']=='UNAVAILABLE'
        conn.rollback()
    checks.append('Locked site skipped without waiting or duplicate work')
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(lambda _:work(),range(2)))
    assert sum(r['accepted'] for r in results)==2,results
    assert sql("select count(*) from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='ORDER'",w=ware)==[(2,)]
    for body in first:
        detail=base.expect(200,base.http('GET',path+'/messages/'+body['event_id'],actor=actor,password=password))
        assert detail['result']['status']=='WAITING' and detail['current_result']['status']=='ACCEPTED',detail
    assert work()['processed']==0
    checks.append('Two workers resolve each document once; original receipts remain waiting')
    rolled,answer=send('ROLL',dict(order,lines=[dict(line,sku_id='B')]))
    assert answer['status']=='WAITING'
    send('B',dict(entity_type='SKU',title='Article B',units_per_box=10,permitted_mrc=['200']))
    with oracle_connection() as conn:
        assert work(TradeDeferredWorker(TransactionGateway(conn.cursor())))['accepted']==1
        conn.rollback()
    assert sql('select STATE from RRL_TRADE_DEFERRED where WARE_ID=:w and EVENT_ID=:e',w=ware,e=rolled['event_id'])==[('WAITING',)]
    assert work()['accepted']==1
    checks.append('Caller rollback restores queue, document and resolution; later worker succeeds')
    financial=dict(schema_version=1,event_id=uuid4().hex,source_id='SAP_QA',warehouse_id=ware,document_id='FIN',version=1,
                   occurred_at=datetime.now(timezone.utc).isoformat(),payload=dict(order,order_kind='BUYOUT',buyout_mode='BEFORE_PICK',lines=[dict(line,sku_id='FIN',uom='EA')]))
    assert base.expect(200,base.http('POST','/api/tradecase/messages',financial))['status']=='WAITING'
    send('FIN',dict(entity_type='SKU',title='Financial article',units_per_box=10,permitted_mrc=['200']))
    assert work()['processed']==0
    assert sql('select ATTEMPTS from RRL_TRADE_DEFERRED where WARE_ID=:w and EVENT_ID=:e',w=ware,e=financial['event_id'])==[(0,)]
    with oracle_connection() as conn:
        cur=conn.cursor();cur.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION) values(:r,'tradecase_buyout_basis_import')",r=f['role']);conn.commit()
    assert work()['accepted']==1
    checks.append('Financial basis skipped without its permission and accepted only after explicit grant')
    with oracle_connection() as conn:
        cur=conn.cursor();cur.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:id',id=f['role']);conn.commit()
    try: work()
    except Exception as exc: assert getattr(exc,'status',None)==403,type(exc).__name__
    else: raise AssertionError('Revoked actor admitted')
    checks.append('Revoked role denied even for an empty queue')
    assert sql('select count(*) from RRL_PALLETS')==[(f['physical_before'],)]
    assert sql("select count(*) from user_objects where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%'")==[(0,)]
    report['slow_sql']=sql('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 30 rows only',n=f['slow_marker'])
    checks.append('No physical stock changes; INVALID zero')


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    f=base.make_fixture()
    report=dict(status='FAIL',fixture={k:v for k,v in f.items()if k!='password'},checks=[],batches=[])
    try:
        run(f,report);report['status']='PASS'
    except Exception as exc:
        report['error_type']=type(exc).__name__;report['error']=str(exc);raise
    finally:
        with oracle_connection() as conn:
            cur=conn.cursor();cur.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC19QA'",a=f['actor'])
            cur.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp) where ASSIGNMENT_ID=:id and USERNAME=:a',id=f['role'],a=f['actor']);conn.commit()
        report['qa_retired']=True;report['http']=base.CALLS
        target=OUT/('deferred-worker-'+str(f['warehouse_id'])+'.json')
        target.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(target))))