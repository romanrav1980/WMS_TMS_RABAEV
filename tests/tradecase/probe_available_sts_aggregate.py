"""Read-only comparison of two existing pagination strategies; never changes product SQL."""
from datetime import date
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.transport.infrastructure.available_sts_query import available_sts_query
from app.modules.transport.infrastructure.available_sts_page import _window

report={'status':'RUNNING','comparisons':[], 'product_changed':False}
path=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T12/available-sts-aggregate-probe.json'
with oracle_connection() as connection:
    q=connection.cursor(); q.execute('set transaction read only')
    q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
    assert q.fetchone()==('RABAEV','orcl')
    for filters in [dict(page=1,page_size=100,ware_id=7),dict(page=2,page_size=100,ware_id=7),
                    dict(page=1,page_size=100),dict(page=2,page_size=20),
                    dict(page=1,page_size=100,stdate=date(2026,5,23))]:
        current,binds=available_sts_query(**filters)
        unpaged,args=available_sts_query(**{k:v for k,v in filters.items() if k not in ('page','page_size')})
        args.update(page_end=filters['page']*filters['page_size'],page_offset=(filters['page']-1)*filters['page_size'])
        variants={'current':(current,binds), 'aggregate':(_window(unpaged),args)}
        samples={key:[] for key in variants}; expected=None
        for repeat in range(5):
            for key in list(variants) if repeat%2==0 else list(reversed(variants)):
                sql,params=variants[key]; began=time.perf_counter(); q.execute(sql,params)
                names=[c[0] for c in q.description]; rows=q.fetchall()
                material=[{k:v for k,v in zip(names,row) if k!='PAGE_ROW_NUMBER'} for row in rows]
                if expected is None: expected=material
                assert material==expected, (filters,key,'ROWS_CHANGED')
                if repeat: samples[key].append(round((time.perf_counter()-began)*1000,2))
        result=dict(filters=filters,rows=len(expected),sha=hashlib.sha256(json.dumps(expected,default=str,sort_keys=True).encode()).hexdigest(),
                    samples=samples,median_ms={key:statistics.median(values) for key,values in samples.items()})
        report['comparisons'].append(result)
        path.write_text(json.dumps(report,default=str,indent=2),encoding='utf-8')
        print(json.dumps(dict(filters=filters,median_ms=result['median_ms']),default=str),flush=True)
    connection.rollback()
report['status']='ROWS_MATCH_NOT_DEPLOYED'
path.write_text(json.dumps(report,default=str,indent=2),encoding='utf-8')
