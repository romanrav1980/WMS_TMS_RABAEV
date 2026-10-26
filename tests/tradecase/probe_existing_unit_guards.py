"""Anonymous old/new lock implementations: technical guards only, no warehouse command."""
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from tools.mcp.tms_mcp_server import oracle_connection

KIT=ROOT/'db/migrations/2026-10-26_existing_unit_guards'
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale'


def program(file,inject=''):
    text=(KIT/file).read_text(encoding='utf-8')
    body=text.split(' as\n',1)[1].rsplit('\nend;',1)[0]
    if inject:
        marker='  -- Missing-key creation keeps numeric native-mutex order, including hash collisions.'
        assert body.count(marker)==1
        body=body.replace(marker,inject+'\n'+marker)
    return 'declare\n'+body+"\nbegin begin_plan;acquire_policies('[]');acquire_resources(:wire);:held:=g_held.count;end;"


def acquire(conn,code,plan):
    cur=conn.cursor();cur.setinputsizes(wire=oracledb.DB_TYPE_CLOB)
    held=cur.var(int);start=time.perf_counter()
    cur.execute(code,wire=json.dumps(plan),held=held)
    return dict(ms=round((time.perf_counter()-start)*1000,2),held=int(held.getvalue()))


def run():
    old,new=program('before_body.sql'),program('001_body.sql')
    report=dict(mode='ANONYMOUS_CODE_PROTOTYPE; NOT_APPLIED; no physical writes',checks=[])
    with oracle_connection()as a,oracle_connection()as b:
        a.call_timeout=b.call_timeout=20000
        q=a.cursor()
        def key(kind,value):
            q.execute('select rawtohex(RRL_STOCK_LOCK_API.resource_key(:k,:v))from dual',k=kind,v=value)
            return q.fetchone()[0]
        token='TC26.UNIT.GUARD.'+uuid4().hex
        existing=dict(rank=60,key_hex=key('UNIT',token))
        # Commit only one owned technical guard; no physical unit or stock row is created.
        acquire(a,old,[existing]);a.commit()
        q.execute("select rawtohex(RRL_STOCK_LOCK_API.resource_key('UNIT',u.PHYSICAL_UNIT_KEY))from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL where c.WARE_ID=225290508 order by u.PHYSICAL_UNIT_KEY")
        actual=[dict(rank=60,key_hex=row[0])for row in q.fetchall()];assert len(actual)==6600;a.rollback()
        try:
            for name,code in [('old',old),('new',new)]:
                measured=acquire(a,code,actual);assert measured['held']==6600
                a.rollback();report['checks'].append(dict(test='6600 committed real UNIT guards',code=name,**measured))
            for holder,waiter in [('old','new'),('new','old'),('new','new')]:
                acquire(a,old if holder=='old'else new,[existing])
                try:
                    acquire(b,old if waiter=='old'else new,[existing])
                    raise AssertionError('Concurrent sessions both acquired the same guard')
                except oracledb.DatabaseError as error:
                    assert error.args[0].code==54,str(error)
                    report['checks'].append(dict(test='Existing UNIT remains exclusive',holder=holder,waiter=waiter,error=str(error)))
                finally:b.rollback();a.rollback()
            for holder,waiter in [('old','new'),('new','old')]:
                missing=dict(rank=60,key_hex=key('UNIT',token+'.missing'))
                acquire(a,old if holder=='old'else new,[missing])
                start=time.perf_counter()
                try:
                    acquire(b,old if waiter=='old'else new,[missing])
                    raise AssertionError('Missing-key native mutex was skipped')
                except oracledb.DatabaseError as error:
                    assert error.args[0].code==20840,str(error)
                    report['checks'].append(dict(test='Missing UNIT keeps native mutex',holder=holder,waiter=waiter,ms=round((time.perf_counter()-start)*1000,2),error=str(error)))
                finally:b.rollback();a.rollback()
            # Inject disappearance after the mutex snapshot; verify whole-command retry instead of silent omission.
            injected="  delete from RRL_STOCK_GUARD where RESOURCE_RANK=60 and RESOURCE_KEY=hextoraw('"+existing['key_hex']+"');"
            try:
                acquire(a,program('001_body.sql',injected),[existing])
                raise AssertionError('Removed UNIT guard was silently skipped')
            except oracledb.DatabaseError as error:
                assert error.args[0].code==20890,str(error)
                report['checks'].append(dict(test='Injected guard removal requires retry',error=str(error)))
            finally:a.rollback()
            # Direct STOCK mutex callers (quality-case API) must still block the new implementation.
            q.execute("select UID_POLETA from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508 and REMAIN>0 fetch first 1 row only")
            stock_key=key('STOCK',q.fetchone()[0]);lock_result=q.var(int)
            q.execute("begin :n:=sys.dbms_lock.request(RRL_STOCK_LOCK_API.resource_lock_id(50,hextoraw(:k)),6,0,true);end;",n=lock_result,k=stock_key);assert lock_result.getvalue()==0
            try:
                acquire(b,new,[dict(rank=50,key_hex=stock_key)])
                raise AssertionError('Direct STOCK mutex caller lost exclusion')
            except oracledb.DatabaseError as error:
                assert error.args[0].code==20840,str(error)
                report['checks'].append(dict(test='Quality-case STOCK mutex compatibility',error=str(error)))
            finally:b.rollback();a.rollback()
        finally:
            b.rollback();a.rollback()
            q.execute('delete from RRL_STOCK_GUARD where RESOURCE_RANK=60 and RESOURCE_KEY=hextoraw(:k)',k=existing['key_hex']);a.commit()
        q.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508');assert q.fetchone()==(6600,0)
        report['stock_unchanged']=[6600,0];report['status']='PASS_PROTOTYPE'
    (OUT/'existing-unit-guard-prototype.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':run()
