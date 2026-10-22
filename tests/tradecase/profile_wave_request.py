"""Time one real owned launch by application call; preserve every native fence and commit."""
from contextlib import contextmanager
from hashlib import sha256
import json,os,re,sys
from pathlib import Path
from time import perf_counter
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
os.environ.setdefault('WMS_ORACLE_PASSWORD','RABAEVWMS')
import profile_case_request as stages
from app.modules.inventory.infrastructure import stock_posting_uow as uow
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T12';OUT.mkdir(exist_ok=True)
RUN=os.environ.get('TRADECASE_WAVE_PROFILE_RUN','');assert not RUN or re.fullmatch(r'[A-Za-z0-9_-]{1,20}',RUN)
TAG='WP22'+('.'+RUN if RUN else '')
FILE=OUT/('wave-request-'+RUN+'.json'if RUN else 'wave-request-state.json');s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(warehouse=220793322,order=2196,history=[],samples=[])
calls=[];profiles=[];line_profile_active=False;original_attempt=uow._attempt


def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')


def transaction_id(connection):
    q=connection.cursor()
    try:
        value=q.var(str,100);q.execute('begin :value:=dbms_transaction.local_transaction_id(false);end;',value=value)
        return value.getvalue()
    finally:q.close()


@contextmanager
def line_profile(connection,kind):
    if not line_profile_active:
        yield None;return
    assert transaction_id(connection)is None,'Do not profile a pre-existing business transaction'
    q=connection.cursor();run=q.var(int)
    q.callproc('DBMS_PROFILER.START_PROFILER',[TAG+'.'+kind,'Owned launch; no bind values',run])
    connection.commit()  # Only profiler setup; no business transaction exists yet.
    number=int(run.getvalue());profiles.append(dict(run_id=number,phase=kind))
    try:yield number
    finally:
        assert transaction_id(connection)is None,'Do not flush or commit an active business transaction'
        q.callproc('DBMS_PROFILER.STOP_PROFILER');connection.commit();q.close()


def step(key,path,body):
    if key not in s:s[key]=expect(200,http('POST',path,body));save()
    return s[key]


class Cursor:
    def __init__(self,raw,kind):object.__setattr__(self,'raw',raw);object.__setattr__(self,'kind',kind)
    def __getattr__(self,key):return getattr(self.raw,key)
    def __setattr__(self,key,value):setattr(self.raw,key,value)
    def execute(self,sql,*args,**kwargs):
        start=perf_counter()
        try:return self.raw.execute(sql,*args,**kwargs)
        finally:
            label='PREPARE'if 'RRL_STOCK_POSTING_API.prepare_command'in sql else 'EXECUTE'if 'RRL_STOCK_POSTING_API.execute_prepared'in sql else 'SQL'
            calls.append(dict(command=self.kind,stage=label,sql_sha256=sha256(sql.encode()).hexdigest(),ms=round((perf_counter()-start)*1000,3)))
    def callproc(self,name,*args,**kwargs):
        start=perf_counter()
        try:return self.raw.callproc(name,*args,**kwargs)
        finally:calls.append(dict(command=self.kind,stage=name,ms=round((perf_counter()-start)*1000,3)))


class Connection:
    def __init__(self,raw,kind):object.__setattr__(self,'raw',raw);object.__setattr__(self,'kind',kind)
    def __getattr__(self,key):return getattr(self.raw,key)
    def __setattr__(self,key,value):setattr(self.raw,key,value)
    def cursor(self,*args,**kwargs):return Cursor(self.raw.cursor(*args,**kwargs),self.kind)
    def commit(self):
        start=perf_counter()
        try:return self.raw.commit()
        finally:calls.append(dict(command=self.kind,stage='COMMIT',ms=round((perf_counter()-start)*1000,3)))


@contextmanager
def measured_metadata_lease():
    with stages.measured_lease()as connection:
        with line_profile(connection,'METADATA')as run:
            stages.events[-1]['profile_run_id']=run
            yield Connection(connection,'METADATA')


def measured_attempt(lease,payload,*args,**kwargs):
    raw=lease.connection;kind=json.loads(payload)['command_type']
    with line_profile(raw,kind)as run:
        lease.connection=Connection(raw,kind);start=perf_counter()
        try:return original_attempt(lease,payload,*args,**kwargs)
        finally:lease.connection=raw;calls.append(dict(command=kind,stage='ATTEMPT_TOTAL',profile_run_id=run,ms=round((perf_counter()-start)*1000,3)))


def measured_log(self,connection,sql,params,started,row_count,error_text,operation_kind):
    stages.measured_log(self,connection,sql,params,started,row_count,error_text,operation_kind)
    if operation_kind=='TRANSACTION':stages.events[-1]['stage']=sql


def prepare():
    with oracle_connection()as c:
        q=c.cursor();q.execute("select NAME from RRL_WARES where ID=220793322");assert q.fetchone()==('TRADECASE QA a4b16acd',)
        q.execute('select STATUS,WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=2196');assert q.fetchone()==('OPEN',220793322)
    step('plan','/api/picking/plans',dict(operation_id=TAG+'.PLAN.2196',customer_order_id=s['order']))
    step('wave','/api/picking/waves',dict(wave_code=TAG+'.2196',wave_name='Owned fresh launch request timing',ware_id=s['warehouse'],planned_start_at='2026-10-22T08:00:00+03:00',planned_finish_at='2026-10-22T09:00:00+03:00'))
    base=f"/api/picking/waves/{s['wave']['pick_wave_id']}"
    step('added',base+'/plans',dict(pick_plan_id=s['plan']['pick_plan_id']));step('calculated',base+'/calculate',{})
    return base


def profile(base):
    global line_profile_active
    if s.get('samples'):return
    from fastapi.testclient import TestClient
    with patch.object(stages.oracle_gateway,'oracle_connection',measured_metadata_lease),patch.object(stages.oracle_gateway.OracleGateway,'_log_slow_sql',measured_log),patch.object(uow,'_attempt',measured_attempt):
        client=TestClient(stages.app)
        for i in range(4):
            line_profile_active=i==0 and os.environ.get('TRADECASE_PLSQL_PROFILE')=='1'
            stages.events.clear();calls.clear();profiles.clear();start=perf_counter()
            r=client.post(base+'/launch',json=dict(operation_id=TAG+'.LAUNCH.2196'),auth=('admin',os.environ['TRADECASE_ADMIN_PASSWORD']))
            sample=dict(round=i,http=r.status_code,total_ms=round((perf_counter()-start)*1000,3),leases=list(stages.events),native_calls=list(calls),profiles=list(profiles),response=r.json())
            s['samples'].append(sample);save();assert r.status_code==200,sample['response']
            assert sample['response']==s['samples'][0]['response'],'Launch receipt changed'
        line_profile_active=False


def cleanup(base):
    wave=s['wave']['pick_wave_id']
    with oracle_connection()as c:
        q=c.cursor();q.execute('select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w order by CASE_PICK_TASK_ID',w=wave);rows=q.fetchall();assert len(rows)==1,rows
    task,carrier,version=rows[0]
    step('cancelled',f'/api/case-pick/tasks/{task}/return-carrier',dict(operation_id=TAG+'.CANCEL.2196',scan_container=carrier,expected_content_version=version,destinations={},allow_empty=True,reason='End owned fresh-wave profile without a physical pick'))
    step('finished',base+'/finish-execution',dict(operation_id=TAG+'.FINISH.2196',disposition='RETURNED_TO_PLANNING',reason='Preserve original two-unit demand after profiling without picking'))
    with oracle_connection()as c:
        q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=220793322');s['stock_after']=list(q.fetchone());assert s['stock_after']==[8,4]
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()[0]==0


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        if s.get('status')!='PASS':
            base=prepare();profile(base);cleanup(base);s['status']='PASS';save()
        print(json.dumps(dict(status=s['status'],wave=s['wave']['pick_wave_id'],stock=s['stock_after'],timings=[v['total_ms']for v in s['samples']])))
    except Exception as exc:s['error']=str(exc);save();raise
    finally:s['history']+=CALLS;save()
