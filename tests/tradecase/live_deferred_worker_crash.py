"""Kill an isolated real worker before/after commit; metadata-only inbound queue, no goods."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/tradecase'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault('TRADECASE_ADMIN_USER','admin')
os.environ.setdefault('TRADECASE_ADMIN_PASSWORD','admin123')
from tools.mcp.tms_mcp_server import oracle_connection
from api.wms_api_server.app.oracle_gateway import OracleGateway
from api.wms_api_server.app.transaction_gateway import TransactionGateway
from api.wms_api_server.app.modules.integrations.infrastructure.trade_deferred_worker import TradeDeferredWorker
import live_document_acceptance as base

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T02'

def child(mode, ware, actor, marker):
    class Cursor:
        def __init__(self, actual): self.actual=actual; self.retried=0
        def __getattr__(self, name): return getattr(self.actual, name)
        def callproc(self, name, args):
            answer=self.actual.callproc(name,args)
            if name=='RRL_TRADE_DOCUMENT_API.retry_document':
                self.retried+=1
                if mode=='before' and self.retried==3:
                    Path(marker).write_text('three native retries executed; not committed',encoding='utf-8')
                    while True: time.sleep(0.2)
            return answer
    with oracle_connection() as connection:
        service=TradeDeferredWorker(TransactionGateway(Cursor(connection.cursor())))
        answer=service.reconcile(ware,actor,25)
        assert answer['accepted']==25,answer
        connection.commit()
        Path(marker).write_text(json.dumps(answer),encoding='utf-8')
        while True: time.sleep(0.2)

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    f=base.make_fixture(); ware,actor,password=f['warehouse_id'],f['actor'],f['password']
    report=dict(status='FAIL',warehouse=ware,actor=actor,checks=[],batches=[],physical_receipts=0,
                queue_size=128,external='Synthetic source messages; actual Oracle and worker processes')
    path=OUT/f'deferred-crash-{ware}.json'
    def save(): path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    def query(sql,**binds):
        with oracle_connection() as connection:
            q=connection.cursor();q.execute(sql,binds);return q.fetchall()
    def send(key,payload):
        return base.expect(200,base.http('POST','/api/tradecase/messages',dict(
            schema_version=1,event_id=f'CRASH23.{ware}.{key}',source_id='SAP_QA',warehouse_id=ware,
            document_id=key,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=payload),actor,password))
    def crash(mode):
        marker=OUT/f'crash-{ware}-{mode}.txt'
        proc=subprocess.Popen([sys.executable,__file__,'--child',mode,str(ware),actor,str(marker)],
                              cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            deadline=time.monotonic()+35
            while not marker.exists() and proc.poll() is None and time.monotonic()<deadline: time.sleep(0.1)
            assert marker.exists(),('Child did not reach boundary',proc.poll())
            report['checks'].append(dict(boundary=mode,marker=marker.read_text(encoding='utf-8')))
        finally:
            if proc.poll() is None: proc.kill()
            _,stderr=proc.communicate(timeout=10)
            assert not stderr,stderr.decode(errors='replace')
        save()
    try:
        base.expect(200,base.http('PUT',f'/api/tradecase/warehouses/{ware}/site',dict(
            operation_id='CRASH23.setup',expected_version=0,source_id='SAP_QA',active_skm='SAP_QA',
            planning_source='SAP',enabled=True,reason='Own metadata queue crash acceptance')))
        for owner in ('SNS','BLC'): send(owner,dict(entity_type='OWNER',title=owner))
        send('C',dict(entity_type='RECIPIENT',title='Own crash queue recipient',target_owner_id='BLC',
                     permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',lead_time_days=1,min_osg_days=0))
        for i in range(report['queue_size']):
            result=send(f'O{i:03}',dict(entity_type='ORDER',recipient_id='C',planned_ship_at='2026-10-24T12:00:00+03:00',
                lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',
                            mrc='200',quantity='1',uom='BOX',min_osg_days=0)]))
            assert result['status']=='WAITING',result
        report['initial']=query('select STATE,count(*),sum(ATTEMPTS)from RRL_TRADE_DEFERRED where WARE_ID=:w group by STATE',w=ware)
        assert report['initial']==[('WAITING',128,0)]
        send('A',dict(entity_type='SKU',title='Own metadata article',units_per_box=10,permitted_mrc=['200']))
        crash('before')
        assert query('select STATE,count(*),sum(ATTEMPTS)from RRL_TRADE_DEFERRED where WARE_ID=:w group by STATE',w=ware)==[('WAITING',128,0)]
        assert query("select count(*)from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='ORDER'",w=ware)==[(0,)]
        report['checks'].append('Process killed after three native retries: complete uncommitted batch rolled back')
        crash('after')
        assert query("select count(*)from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='ORDER'",w=ware)==[(25,)]
        worker=TradeDeferredWorker(OracleGateway())
        accepted=0
        for i in range(10):
            began=time.perf_counter(); value=worker.reconcile(ware,actor,25)
            report['batches'].append(dict(ms=round((time.perf_counter()-began)*1000,2),result=value));save()
            accepted+=value['accepted']
            if value['processed']==0: break
        assert accepted==103,accepted
        assert query("select count(*)from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='ORDER'",w=ware)==[(128,)]
        assert query('select STATE,count(*),min(ATTEMPTS),max(ATTEMPTS)from RRL_TRADE_DEFERRED where WARE_ID=:w group by STATE',w=ware)==[('ACCEPTED',128,1,1)]
        # Original incoming receipt stays WAITING; current resolution is stored separately.
        detail=base.expect(200,base.http('GET',f'/api/tradecase/warehouses/{ware}/messages/CRASH23.{ware}.O000',actor=actor,password=password))
        assert detail['result']['status']=='WAITING' and detail['current_result']['status']=='ACCEPTED'
        report['checks'].append('Kill after commit/lost output: restart drains remaining103,128 accepted exactly once, original receipt unchanged')
        assert query('select count(*)from RRL_PALLETS')==[(f['physical_before'],)]
        assert query("select count(*)from user_objects where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'")==[(0,)]
        report['slow_sql']=query('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 40 rows only',n=f['slow_marker'])
        report['status']='PASS'
    except Exception as exc:
        report.update(error_type=type(exc).__name__,error=str(exc));raise
    finally:
        with oracle_connection() as connection:
            q=connection.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC19QA'",a=actor)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=f['role'])
            connection.commit()
        report['retired']=True;report['http']=base.CALLS;save()
    print(json.dumps(dict(status=report['status'],warehouse=ware,evidence=str(path))))

if __name__=='__main__':
    if '--child' in sys.argv: child(sys.argv[2],int(sys.argv[3]),sys.argv[4],sys.argv[5])
    else: run()
