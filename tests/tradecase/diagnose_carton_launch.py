"""Time native prepare/execute separately and roll back the entire owned command."""
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


def run():
    output=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/launch-native-budget8.json'
    assert not output.exists(),'Preserve previous diagnostic evidence'
    report=dict(mode='NATIVE_PREPARE_EXECUTE_ROLLBACK; diagnostic call limit 45s, HTTP stays 30s')
    command=StockCommand(operation_id='TP26.e9508cd7.launch.places1000',command_type='WAVE_LAUNCH',actor='admin',lines=(),source={'wave_id':636},metadata={})
    with oracle_connection()as conn:
        cur=conn.cursor();conn.call_timeout=45000
        cur.execute('select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=command.operation_id);assert cur.fetchone()is None
        cur.execute('select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=636');assert cur.fetchone()[0]=='PREVIEW'
        cur.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508');assert cur.fetchone()==(6600,0)
        conn.rollback()
        payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,command.canonical_json());replay=cur.var(oracledb.DB_TYPE_CLOB);resolution=cur.var(oracledb.DB_TYPE_CLOB);result=cur.var(oracledb.DB_TYPE_CLOB)
        stage='prepare';start=time.perf_counter()
        try:
            cur.callproc('RRL_STOCK_POSTING_API.prepare_command',[payload,'admin',replay,resolution])
            report['prepare_ms']=round((time.perf_counter()-start)*1000,2)
            cur.execute('select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=command.operation_id);row=cur.fetchone();assert row
            value=row[0].read()if hasattr(row[0],'read')else row[0];plan=json.loads(value)
            report['resource_count']=len(plan['resources']);report['policy_count']=len(plan['policies'])
            (output.parent/'prepare-resolved-plan-budget8.json').write_text(json.dumps(plan),encoding='utf-8')
            stage='execute';start=time.perf_counter();cur.callproc('RRL_STOCK_POSTING_API.execute_prepared',[result]);report['execute_ms']=round((time.perf_counter()-start)*1000,2)
            value=result.getvalue();report['result']=json.loads(value.read()if hasattr(value,'read')else value)
            cur.execute('select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=636');report['before_rollback_wave']=cur.fetchone()[0]
        except Exception as error:
            report.update(error_stage=stage,error=str(error),failed_stage_ms=round((time.perf_counter()-start)*1000,2))
        finally:
            conn.rollback();cur.callproc('RRL_STOCK_POSTING_API.reset_connection')
        cur.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508');report['after']=cur.fetchone();assert report['after']==(6600,0)
        cur.execute('select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=636');assert cur.fetchone()[0]=='PREVIEW'
        cur.execute('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o',o=command.operation_id);assert cur.fetchone()[0]==0
        report['status']='ROLLED_BACK_UNCHANGED'
    output.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))


if __name__=='__main__':run()
