"""Hold one owned wave mutex; verify bounded refusal and unchanged inventory."""
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection


def run():
    report={}
    with oracle_connection()as holder,oracle_connection()as waiter:
        a=holder.cursor();b=waiter.cursor();holder.call_timeout=12000;waiter.call_timeout=12000
        a.execute("select rawtohex(RRL_STOCK_LOCK_API.resource_key('ROW','RRL_PICK_WAVE','636'))from dual")
        plan=json.dumps([dict(rank=20,key_hex=a.fetchone()[0])])
        def stock(cur):
            cur.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508')
            return cur.fetchone()
        before=stock(a);holder.rollback()
        try:
            a.callproc('RRL_STOCK_LOCK_API.begin_plan');a.callproc('RRL_STOCK_LOCK_API.acquire_policies',['[]']);a.callproc('RRL_STOCK_LOCK_API.acquire_resources',[plan])
            b.callproc('RRL_STOCK_LOCK_API.begin_plan');b.callproc('RRL_STOCK_LOCK_API.acquire_policies',['[]'])
            start=time.perf_counter()
            try:
                b.callproc('RRL_STOCK_LOCK_API.acquire_resources',[plan])
                raise AssertionError('Second session acquired an occupied exclusive mutex')
            except Exception as error:
                assert 'ORA-20840' in str(error),str(error)
                report['error']=str(error);report['elapsed_ms']=round((time.perf_counter()-start)*1000,2)
                assert 6000<=report['elapsed_ms']<11000
        finally:
            waiter.rollback();b.callproc('RRL_STOCK_LOCK_API.clear_plan')
            holder.rollback();a.callproc('RRL_STOCK_LOCK_API.clear_plan')
        b.callproc('RRL_STOCK_LOCK_API.begin_plan');b.callproc('RRL_STOCK_LOCK_API.acquire_policies',['[]']);b.callproc('RRL_STOCK_LOCK_API.acquire_resources',[plan]);waiter.rollback();b.callproc('RRL_STOCK_LOCK_API.clear_plan')
        assert stock(a)==before
        report.update(status='PASS',stock_unchanged=before,acquired_after_release=True)
    path=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/lock-contention-budget8.json';path.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))


if __name__=='__main__':run()
