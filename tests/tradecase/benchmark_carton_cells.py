"""Read-only native cell validation and frozen before-quantity query timings."""
import json
from pathlib import Path
import re
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection


def run():
    label=sys.argv[1];assert re.fullmatch('[a-z0-9-]{1,40}',label)
    out=ROOT/('runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/cell-check-'+label+'.json');assert not out.exists()
    report=dict(scope='READ_ONLY native cell checks, 40 owned cells, one sequential pass',samples=[])
    with oracle_connection()as conn:
        cur=conn.cursor();cur.execute("select distinct CURRENT_CELL from RRL_WMS_RECEIPT_UNIT where CURRENT_UID like 'CT26.225290508.%'order by CURRENT_CELL fetch first 40 rows only");cells=[r[0]for r in cur.fetchall()];assert len(cells)==40
        for cell in cells:
            start=time.perf_counter();cur.callproc('RRL_TRADE_STOCK_GUARD.assert_cell',[cell]);report['samples'].append(dict(cell=cell,ms=round((time.perf_counter()-start)*1000,3)))
        cur.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=225290508');report['stock']=cur.fetchone();assert report['stock']==(6600,0)
    values=[x['ms']for x in report['samples']];report.update(status='PASS',median_ms=statistics.median(values),max_ms=max(values),total_ms=sum(values))
    out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='samples'}))


if __name__=='__main__':run()
