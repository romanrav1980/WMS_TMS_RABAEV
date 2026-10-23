"""Read-only Oracle comparison of legacy page expansion, indexed expansion and NULL-key fixtures."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'api/wms_api_server'),str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.transport.infrastructure.available_sts_query import available_sts_query
from itertools import product

def _page_pallets() -> str:
    columns = ",".join("P."+name for name in (
        "ID", "ST_NUMBER", "ADDR", "WARE_ID", "NAPR", "PALLET_UID", "STDATE", "TRANSTASK_ID",
        "ZONE", "ZONE_TIME_PLAN_IN", "ZONE_TIME_PLAN_OUT", "PROOVED", "PROOVED_BY_SCAN", "CONDITION"))
    # One explicitly filtered warehouse excludes NULL WARE_ID through its IN predicate.
    branches = []
    for nulls in product((False, True), repeat=2):
        predicates = ["P."+name+" IS NULL AND K."+name+" IS NULL" if is_null else "P."+name+"=K."+name
                      for name, is_null in zip(("ST_NUMBER", "ADDR"), nulls)]
        predicates.append("P.WARE_ID=K.WARE_ID")
        branches.append("select "+columns+" from RABAEV.RRL_SBORKA_PALLETS P where "+" AND ".join(predicates))
    return "K CROSS APPLY ("+" UNION ALL ".join(branches)+") P"



OLD="K JOIN RABAEV.RRL_SBORKA_PALLETS P ON (P.ST_NUMBER=K.ST_NUMBER OR (P.ST_NUMBER IS NULL AND K.ST_NUMBER IS NULL)) AND DECODE(P.ADDR,K.ADDR,1,0)=1 AND DECODE(P.WARE_ID,K.WARE_ID,1,0)=1"
report=dict(status='FAIL',comparisons=[],fixture_checks=[],unscoped_unchanged=[])
prefix="""with QA_P as(select ID,ST_NUMBER,ADDR,WARE_ID,PALLET_UID,CONDITION,
 cast(null as varchar2(30))NAPR,date'2026-10-23'STDATE,cast(null as number)TRANSTASK_ID,
 cast(null as varchar2(30))ZONE,cast(null as date)ZONE_TIME_PLAN_IN,cast(null as date)ZONE_TIME_PLAN_OUT,
 0 PROOVED,0 PROOVED_BY_SCAN from json_table(:fixture,'$[*]'columns(
 ID number path'$.id',ST_NUMBER varchar2(30)path'$.st',ADDR varchar2(30)path'$.addr',
 WARE_ID number path'$.ware',PALLET_UID varchar2(30)path'$.uid',CONDITION number path'$.condition'))),
 QA_R as(select PALLET_UID,1 ORDER_WEIGHT,1 TARESIZE,1 PACK_COUNT,'QA' ARTICUL from QA_P),
 QA_A as(select cast(null as varchar2(30))ADDR,cast(null as varchar2(30))REGION,
 cast(null as varchar2(30))RAION,cast(null as number)ORD,cast(null as varchar2(20))TRANSPORT_TYPE,
 cast(null as number)STOL,cast(null as varchar2(100))PRIM1 from dual where 1=0)
 """
fixture=json.dumps([dict(id=i,st=st,addr=addr,ware=ware,uid='U'+str(i)if i!=8 else None,condition=condition)
 for i,st,addr,ware,condition in [(1,None,None,None,0),(2,None,None,None,0),(3,None,'X',None,0),
 (4,'S',None,7,0),(5,'S',None,8,0),(6,'S',None,7,2),(7,'Q','X',7,0),(8,'Z',None,None,0),
 (9,None,None,7,0),(10,None,'X',7,0)]])

def synthetic(sql):
    for table,replacement in [('RRL_SBORKA_PALLET_ROWS','QA_R'),('RRL_SBORKA_PALLETS','QA_P'),('RRL_ADDR','QA_A')]:
        sql=sql.replace('RABAEV.'+table,replacement)
    return prefix+sql

with oracle_connection()as connection:
    q=connection.cursor();q.execute('set transaction read only')
    q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
    for filters in [dict(page=1,page_size=100),dict(page=2,page_size=100),dict(page=1,page_size=100,ware_ids=[7,8])]:
        unchanged,_=available_sts_query(**filters);assert _page_pallets()not in unchanged and OLD in unchanged
        report['unscoped_unchanged'].append(filters)
    for filters in [dict(page=1,page_size=100,ware_id=7),dict(page=2,page_size=100,ware_id=7),
                    dict(page=3,page_size=20,ware_ids=[7])]:
        old,params=available_sts_query(**filters);new=old.replace(OLD,_page_pallets(),1);assert _page_pallets()in new
        old=new.replace(_page_pallets(),OLD,1);samples={'old':[],'new':[]};expected=None
        for repeat in range(5):
            for label,sql in [('old',old),('new',new)]if repeat%2==0 else [('new',new),('old',old)]:
                start=time.perf_counter();q.execute(sql,params);rows=q.fetchall()
                if expected is None:expected=rows
                assert rows==expected,(filters,label,'ROWS_CHANGED')
                if repeat:samples[label].append(round((time.perf_counter()-start)*1000,2))
        report['comparisons'].append(dict(filters=filters,rows=len(expected),sha=hashlib.sha256(json.dumps(expected,default=str).encode()).hexdigest(),
                median_ms={k:statistics.median(v)for k,v in samples.items()},samples_ms=samples))
    unpaged,params=available_sts_query()
    q.execute(synthetic(unpaged),dict(params,fixture=fixture));expected=q.fetchall();assert len(expected)==7
    for filters in [dict(page=1,page_size=100),dict(page=2,page_size=2),dict(page=1,page_size=100,ware_id=7),dict(page=2,page_size=2,ware_id=7)]:
        old,params=available_sts_query(**filters);new=old.replace(OLD,_page_pallets(),1) if 'wid0'in params and 'wid1'not in params else old
        q.execute(synthetic(old),dict(params,fixture=fixture));old_rows=q.fetchall()
        q.execute(synthetic(new),dict(params,fixture=fixture));new_rows=q.fetchall()
        assert old_rows==new_rows
        if filters.get('ware_id')is None:
            start=(filters['page']-1)*filters['page_size'];assert new_rows==expected[start:start+filters['page_size']]
        else:assert all(row[9]==7 for row in new_rows)
        report['fixture_checks'].append(dict(filters=filters,rows=len(new_rows),match=True))
    connection.rollback()
report['status']='ROWS_MATCH_PERFORMANCE_REJECTED'
out=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T12/available-sts-scoped-probe.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],comparisons=report['comparisons'],null_fixture=report['fixture_checks'])))
