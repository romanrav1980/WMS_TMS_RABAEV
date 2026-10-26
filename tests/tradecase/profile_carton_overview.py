"""Time the existing read-only shift sources on one owned wave and snapshot."""
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.services.picking_service import PickingService
from app.modules.inventory.infrastructure.shift_overview import ShiftOverview,BoundOverviewRead
from app.modules.inventory.public import WavePickRelease,ReplenishmentProgress
from app.modules.resources.public import build_wave_time


def run():
    label=sys.argv[1];assert label.isalnum()
    output=ROOT/('runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/overview-'+label+'.json');assert not output.exists()
    parts=[]
    def timed(name,reader):
        def read(gateway,wave,actor):
            start=time.perf_counter()
            try:return reader(gateway,wave,actor)
            finally:parts.append(dict(source=name,ms=round((time.perf_counter()-start)*1000,3)))
        return read
    readers={
        'readiness':lambda g,w,a:PickingService(g).get_wave_readiness(w),
        'pick':lambda g,w,a:WavePickRelease(g).preview(w,a),
        'time':lambda g,w,a:build_wave_time(g).context(w,a),
        'replenishment':lambda g,w,a:ReplenishmentProgress(g).list_rows(w,100)}
    with oracle_connection()as conn:
        cur=conn.cursor()
        result=ShiftOverview(BoundOverviewRead(cur),{k:timed(k,v)for k,v in readers.items()}).read('admin',225290508,[636])
        assert result['commands_executed']is False and result['stock_changed']is False
        conn.rollback()
    report=dict(scope='One READ ONLY snapshot; warehouse225290508/wave636, no mutation',parts=parts,
                source_statuses={k:v['status']for k,v in result['waves'][0].items()if k!='wave_id'})
    output.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))


if __name__=='__main__':run()
