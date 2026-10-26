"""Save current owned balances and measured HTTP timings without business writes."""
import json
from pathlib import Path
import re
import statistics
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection


def run():
    label=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',label)
    folder=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/physical'
    output=folder/('report-'+label+'.json');assert not output.exists()
    state=json.loads((folder/'state.json').read_text());calls=list(state.get('http',[]))
    for name in state.get('http_archives',[]):calls.extend(json.loads((folder/name).read_text()))
    groups={}
    for call in calls:
        key=call['method']+' '+re.sub(r'/\d+(?=/|$)','/{id}',call['path'].split('?')[0])+' '+str(call['status'])
        groups.setdefault(key,[]).append(call['elapsed_ms'])
    report=dict(phase=state['phase'],scope='Owned 660-place scale fixture; synthetic masters/weights/external replies, not source 3-order acceptance',
                timings={k:dict(n=len(v),median_ms=statistics.median(v),max_ms=max(v))for k,v in groups.items()},http_calls=len(calls),native={})
    queries={
      'stock':("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w",dict(w=225290508)),
      'warehouse_tasks':("select STATUS,count(*)from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=636 and TASK_TYPE='PICKING_MOVE'group by STATUS",{}),
      'wave':('select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=636',{}),
      'fulfillment':('select STATUS,count(*),sum(FACT_QTY)from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:o group by STATUS',dict(o=state['native_order']['order'])),
      'invalid':("select count(*)from USER_OBJECTS where STATUS='INVALID'",{}),
      'slow_sql':("select LOG_ID,MODULE,ACTION,ELAPSED_MS,substr(SQL_TEXT,1,400)from RRL_SQL_SLOW_LOG where LOG_ID>7066 order by ELAPSED_MS desc fetch first 12 rows only",{})}
    with oracle_connection()as conn:
        cur=conn.cursor();cur.execute('set transaction read only')
        for name,(sql,binds)in queries.items():cur.execute(sql,binds);report['native'][name]=cur.fetchall()
        conn.rollback()
    output.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(phase=report['phase'],native=report['native'],http_calls=len(calls)),default=str))


if __name__=='__main__':run()
