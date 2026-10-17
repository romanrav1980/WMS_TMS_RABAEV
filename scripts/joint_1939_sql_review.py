"""Bounded READ ONLY audit collector. No API calls, request bodies, DDL or business writes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/retailcase/2026-10-15/joint-sql-review.json'
TOKENS=('warehouse-scales','case-pick','picker-time','picker-actual-time','resource-sessions','/api/help/','/api/hu','/api/handling-unit')


def local_audit(path:Path, since:str)->dict[str,Any]:
    """Bounded tail, correlate phases ONLY by explicit request_id; never include bodies/headers."""
    floor=datetime.fromisoformat(since)
    with path.open('rb')as stream:
        stream.seek(0,2);size=stream.tell();start=max(0,size-8*1024*1024);stream.seek(start)
        if start:stream.readline()
        lines=stream.read().splitlines()[-12000:]
    phases:dict[str,dict[str,Any]]={};bad=0
    for line in lines:
        try:
            item=json.loads(line)
            if datetime.fromisoformat(item['logged_at'])<floor:continue
            key=item.get('request_id')
            if not isinstance(key,str)or not key:continue
            safe={k:item[k]for k in ('phase','api_call_id','request_id','method','path','response_status','duration_ms','logged_at')if k in item}
            phases.setdefault(key,{}).update(safe)
        except (ValueError,KeyError,TypeError):bad+=1
    rows=[r for r in phases.values()if any(t in r.get('path','')for t in TOKENS)]
    rows.sort(key=lambda r:r['logged_at'])
    return dict(path=str(path.relative_to(ROOT)),tail_bytes=min(size,8*1024*1024),line_cap=12000,
                invalid_lines=bad,rows=rows[-1000:],truncated=len(rows)>1000,scope='HTTP only; explicit request_id phase join; no native-to-HTTP inference')


def collect(min_api_id:int,since:str)->dict[str,Any]:
    sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.db import oracle_connection
    report:dict[str,Any]=dict(status='COLLECTED_REQUIRES_QUERY_DECISIONS',collected_at=datetime.now(timezone.utc).isoformat(),
      min_api_id=min_api_id,local_since=since,read_only=True,limitations=[
        'Direct native calls have no invented API request pairing.',
        'V$SQL totals are cumulative shared-cursor observations, not per-scenario latency or execution deltas.',
        'Oracle legacy STARTED_AT/CREATED_AT wall timestamps are recorded as-is, not labelled verified UTC.',
        'Bounded samples can omit older rows; zero fresh slow rows is not proof every native nested statement was instrumented.'])
    queries={
      'api':("""select API_CALL_ID,REQUEST_ID,METHOD,PATH,RESPONSE_STATUS,STATUS,DURATION_MS,STARTED_AT
        from RRL_API_CALL_LOG where API_CALL_ID>=:lo order by API_CALL_ID desc fetch first 1500 rows only""",{'lo':min_api_id}),
      'slow_recent':("""select LOG_ID,CREATED_AT,MODULE,ACTION,API_CALL_ID,API_METHOD,API_PATH,ELAPSED_MS,SQL_TEXT_HASH,ROW_COUNT,
        substr(SQL_TEXT,1,1400)SQL_SAMPLE from RRL_SQL_SLOW_LOG
        where LOG_ID>=(select nvl(max(LOG_ID),0)-500 from RRL_SQL_SLOW_LOG)
        order by LOG_ID desc fetch first 501 rows only""",{}),
      'native_relevant_cumulative':("""select SQL_ID,COMMAND_TYPE,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)AVG_MS,
        round(BUFFER_GETS/nullif(EXECUTIONS,0),2)AVG_BUFFERS,LAST_ACTIVE_TIME,substr(SQL_TEXT,1,1400)SQL_SAMPLE
        from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
        and(SQL_TEXT like '%RRL_PICKER_TIME_%'or SQL_TEXT like '%RRL_WH_WEIGH_%'
         or SQL_TEXT like '%RRL_CASE_LIFECYCLE_%'or SQL_TEXT like '%RRL_CASE_PICK_TASK%'
         or SQL_TEXT like '%RRL_STOCK_POSTING_API%'or SQL_TEXT like '%RRL_STOCK_CASE_RETURN%')
        order by ELAPSED_TIME desc fetch first 40 rows only""",{})}
    with oracle_connection()as connection:
        connection.call_timeout=10000
        cursor=connection.cursor()
        try:
            cursor.execute('set transaction read only')
            for name,(sql,binds)in queries.items():
                try:
                    cursor.execute(sql,binds);keys=[d[0].lower()for d in cursor.description]
                    report[name]=[dict(zip(keys,[value.read()if hasattr(value,'read')else value for value in row],strict=True))for row in cursor.fetchall()]
                except Exception as error:report[name+'_error']=type(error).__name__+': '+str(error).splitlines()[0]
        finally:connection.rollback();cursor.close()
    report['local']=local_audit(ROOT/'api/wms_api_server/runtime/api_audit/2026-10-15.jsonl',since)
    ids={r['api_call_id']for r in report.get('api',[])}
    report['slow_http_in_api_sample']=[r for r in report.get('slow_recent',[])if r.get('api_call_id')in ids]
    report['slow_unpaired']=[r for r in report.get('slow_recent',[])if r.get('api_call_id')not in ids]
    report['known_catalog_decision']=dict(evidence='reports/retailcase/2026-10-15/picker-time-source/partial-native-sql-review.json',
       owner='operations/schema verification',decision='Existing backlog: USER_CONSTRAINTS5.9s/catalog gate6.4s; exact named-constraint/batched catalog reads and dictionary-plan/statistics review before broad rollout. Not picking latency; no stock index justified.')
    return report


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--collect-read-only',action='store_true')
    parser.add_argument('--min-api-id',type=int,default=69200);parser.add_argument('--local-since',default='2026-10-15T17:45:00+00:00')
    args=parser.parse_args()
    assert args.min_api_id>0 and datetime.fromisoformat(args.local_since).utcoffset()is not None
    if not args.collect_read_only:print('PREPARED_ONLY: no Oracle/API calls; root finalizes bounded audit after positive lifecycle');return
    assert not OUT.exists(),'Preserve original evidence; use a reviewed distinct output for another collection'
    report=collect(args.min_api_id,args.local_since)
    with OUT.open('x',encoding='utf-8')as stream:json.dump(report,stream,indent=2,default=str)
    print(json.dumps(dict(path=str(OUT),status=report['status'],api_rows=len(report.get('api',[])))))


if __name__=='__main__':main()
