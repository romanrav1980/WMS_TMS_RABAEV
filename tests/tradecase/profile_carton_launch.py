"""Profile preparation only, then roll back. Never execute or commit the warehouse command."""
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.inventory.public import StockCommand

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale'
command=StockCommand(operation_id='TP26.e9508cd7.launch.places1000',command_type='WAVE_LAUNCH',actor='admin',lines=(),source={'wave_id':636},metadata={})


def stock(cur):
    cur.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508')
    return cur.fetchone()


def run():
    result=dict(mode='PREPARE_ONLY_THEN_ROLLBACK; diagnostic 55s call budget, API remains 30s',status='RUNNING')
    with oracle_connection()as conn:
        cur=conn.cursor();conn.call_timeout=55000
        cur.execute("select user,sys_context('USERENV','DB_NAME')from dual");assert cur.fetchone()==('RABAEV','ORCL')
        cur.execute('select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=command.operation_id);assert cur.fetchone()is None
        assert stock(cur)==(6600,0)
        conn.rollback()
        run_id=cur.var(int)
        cur.callproc('DBMS_PROFILER.START_PROFILER',['TC26.CARTON.PREPARE','Owned preparation only; rollback all command effects',run_id])
        conn.commit()  # Only profiler setup; no business transaction exists.
        result['run_id']=int(run_id.getvalue())
        payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,command.canonical_json())
        replay=cur.var(oracledb.DB_TYPE_CLOB);resolved=cur.var(oracledb.DB_TYPE_CLOB)
        start=time.perf_counter()
        try:
            cur.callproc('RRL_STOCK_POSTING_API.prepare_command',[payload,'admin',replay,resolved])
            value=resolved.getvalue();value=value.read()if hasattr(value,'read')else value
            if value:
                plan=json.loads(value);result['resource_count']=len(plan.get('resources',[]));result['policy_count']=len(plan.get('policies',[]))
                (OUT/'prepare-resolved-plan.json').write_text(json.dumps(plan),encoding='utf-8')
            result['prepare']='RETURNED'
        except Exception as error:
            result['prepare_error']=str(error)
        finally:
            result['prepare_ms']=round((time.perf_counter()-start)*1000,2)
            conn.rollback();cur.callproc('RRL_STOCK_POSTING_API.reset_connection')
            cur.callproc('DBMS_PROFILER.STOP_PROFILER');conn.commit()  # Diagnostic rows only, after rollback.
        result['after']=stock(cur);assert result['after']==(6600,0)
        cur.execute('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=command.operation_id);assert cur.fetchone()[0]==0
        cur.execute("""select u.UNIT_NAME,d.LINE#,d.TOTAL_OCCUR,round(d.TOTAL_TIME/1000000,3),round(d.MAX_TIME/1000000,3),s.TEXT
            from PLSQL_PROFILER_UNITS u join PLSQL_PROFILER_DATA d on d.RUNID=u.RUNID and d.UNIT_NUMBER=u.UNIT_NUMBER
            left join USER_SOURCE s on s.NAME=u.UNIT_NAME and s.TYPE=u.UNIT_TYPE and s.LINE=d.LINE#
            where u.RUNID=:r and d.TOTAL_OCCUR>0 order by d.TOTAL_TIME desc fetch first 35 rows only""",r=result['run_id'])
        result['top_lines']=[dict(unit=n,line=line,calls=calls,total_ms=total,max_ms=maximum,source=source)for n,line,calls,total,maximum,source in cur.fetchall()]
        cur.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert cur.fetchone()[0]==0
        result['status']='ROLLED_BACK_UNCHANGED'
    (OUT/'launch-prepare-profile.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
    print(json.dumps({**result,'top_lines':result['top_lines'][:10]},default=str))


if __name__=='__main__':run()
