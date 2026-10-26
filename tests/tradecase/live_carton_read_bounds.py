"""Read-only Oracle regression and native input-bound probes; not physical carton acceptance."""
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'api/wms_api_server'), str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.transport.infrastructure.loading_status import read_loading_status

OUT = ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale'


def old_module(name):
    path = 'api/wms_api_server/app/modules/transport/infrastructure/'+name+'.py'
    source = subprocess.check_output(['git','show','3f26998f:'+path], cwd=ROOT).decode('utf-8')
    module = types.ModuleType(name)
    module.__package__ = 'app.modules.transport.infrastructure'
    exec(compile(source, path, 'exec'), module.__dict__)
    return module


def normalize(value):
    return json.loads(json.dumps(value, default=str, sort_keys=True))


def run():
    old = old_module('loading_status')
    old.loading_floor_read = old_module('loading_floor_read').loading_floor_read
    old.loading_thermal_read = old_module('loading_thermal_read').loading_thermal_read
    report = dict(status='RUNNING', scope='READ_ONLY; duplicate IDs probe input windows, not 660 physical places', trips=[], native=[])
    with oracle_connection() as conn:
        cur = conn.cursor()
        cur.execute("select user,sys_context('USERENV','DB_NAME')from dual")
        assert cur.fetchone() == ('RABAEV','ORCL')
        for trip in [33681,33682,33683,33684,33685,33686]:
            cur.execute('set transaction read only')
            timings = {'old':[], 'new':[]}
            expected = None
            for _ in range(3):
                for label, reader in [('old',old.read_loading_status),('new',read_loading_status)]:
                    started = time.perf_counter()
                    value = normalize(reader(cur, trip, 'admin'))
                    timings[label].append(round((time.perf_counter()-started)*1000,2))
                    if expected is None:
                        expected = value
                    assert value == expected, (trip,label)
            report['trips'].append(dict(trip=trip, equal=True, places=len(expected['physical_places']), timings=timings,
                                       median_ms={key:statistics.median(values) for key,values in timings.items()}))
            conn.rollback()
        cur.execute('set transaction read only')
        cur.execute('select sp.ID,sp.ST_NUMBER,v.ID from RRL_SBORKA_PALLETS sp join RRL_TRANSPORT_TASK t on t.ID=sp.TRANSTASK_ID join RRL_TR_VEHICLE v on v.NUM=t.TRANSPORT where t.ID=33685 order by sp.ID fetch first 1 row only')
        member, st, vehicle = cur.fetchone()
        for count in [200,660,1000,1001]:
            wire = json.dumps([member]*count)
            cur.setinputsizes(members=oracledb.DB_TYPE_CLOB)
            result = cur.var(oracledb.DB_TYPE_CLOB)
            started = time.perf_counter()
            try:
                cur.execute("declare x json_object_t;begin RRL_STOCK_LOAD_THERMAL.compile_confirmation(:members,:vehicle,'{}',x,'MANUAL_AT_DEPARTURE');:result:=case when x is null then null else x.to_clob end;end;",members=wire,vehicle=vehicle,result=result)
                assert count<=1000
                value = result.getvalue(); value = value.read() if hasattr(value,'read') else value
                report['native'].append(dict(count=count, accepted=True, result=json.loads(value) if value else None, elapsed_ms=round((time.perf_counter()-started)*1000,2)))
            except oracledb.DatabaseError as error:
                if 'PLS-00904' in str(error):
                    report['native'].append(dict(count=count, status='NOT_EXECUTED_ACCESSIBLE_BY', error=str(error)))
                    break
                assert count==1001 and 'LOAD_THERMAL_MEMBER_BOUND_1000' in str(error), str(error)
                report['native'].append(dict(count=count, accepted=False, expected_error=str(error)))
        conn.rollback()
        cur.execute("select count(*)from user_objects where status='INVALID'")
        assert cur.fetchone()[0]==0
    report['status']='PASS_READ_REGRESSION'
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'read-regression.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],trips=report['trips'],native=[{k:v for k,v in x.items() if k!='result'}for x in report['native']]),default=str))


if __name__=='__main__':
    run()
