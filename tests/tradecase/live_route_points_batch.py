"""Old/new route point equality and SQL count on closed native trips; no business writes."""
from contextlib import contextmanager
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
import types

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.integrations.infrastructure.trade_route_plan import route_points


class Gateway:
    def __init__(self,conn):self.conn=conn;self.executions=0
    @contextmanager
    def transaction(self,purpose):
        raw=self.conn.cursor();outer=self
        class Cursor:
            def execute(self,*args,**kwargs):outer.executions+=1;return raw.execute(*args,**kwargs)
            def __getattr__(self,name):return getattr(raw,name)
        try:yield Cursor()
        finally:self.conn.rollback();raw.close()


def run():
    module=types.ModuleType('baseline');module.__package__='app.modules.integrations.infrastructure'
    source=subprocess.check_output(['git','show','3f26998f:api/wms_api_server/app/modules/integrations/infrastructure/trade_route_plan.py'],cwd=ROOT).decode('utf-8')
    exec(compile(source,'baseline-route.py','exec'),module.__dict__)
    report=dict(status='RUNNING',trips=[])
    with oracle_connection()as conn:
        cur=conn.cursor();cur.execute('select WARE_ID,TRIP_ID,NATIVE_TASK_ID from RRL_TRADE_TRIP_LINK where NATIVE_TASK_ID in(33681,33682,33683,33684,33685,33686)order by NATIVE_TASK_ID');trips=cur.fetchall();conn.rollback()
        assert len(trips)>=5
        for ware,trip,native in trips:
            expected=None;timings={'old':[],'new':[]};queries={'old':[],'new':[]}
            for _ in range(3):
                for name,reader in [('old',module.route_points),('new',route_points)]:
                    gateway=Gateway(conn);start=time.perf_counter();value=reader(gateway,ware,trip,'admin')
                    timings[name].append(round((time.perf_counter()-start)*1000,2));queries[name].append(gateway.executions)
                    if expected is None:expected=value
                    assert value==expected,(native,name)
            report['trips'].append(dict(warehouse=ware,trip=trip,native=native,points=len(expected['points']),equal=True,elapsed_ms=timings,query_counts=queries,median_ms={k:statistics.median(v)for k,v in timings.items()}))
    report['status']='PASS_READ_ONLY'
    out=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/route-points-batch.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':run()
