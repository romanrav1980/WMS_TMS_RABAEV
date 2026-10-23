"""One read-only instrumented page; capture actual cursor work without changing production SQL."""
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.transport.infrastructure.available_sts_query import available_sts_query

report=dict(status='RUNNING',product_changed=False)
marker='TC23_ST_PROFILE_'+uuid4().hex[:10]
with oracle_connection() as connection:
    cur=connection.cursor();cur.execute('set transaction read only')
    cur.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
    assert cur.fetchone()==('RABAEV','orcl')
    sql,params=available_sts_query(page=1,page_size=100,ware_id=7)
    sql='/* '+marker+' */ '+sql.replace('SELECT','SELECT /*+ gather_plan_statistics */',1)
    began=time.perf_counter();cur.execute(sql,params);rows=cur.fetchall()
    report.update(ms=round((time.perf_counter()-began)*1000,2),rows=len(rows))
    cur.execute('select SQL_ID,CHILD_NUMBER,PLAN_HASH_VALUE,EXECUTIONS,BUFFER_GETS,DISK_READS,CPU_TIME,ELAPSED_TIME,ROWS_PROCESSED '
                'from V$SQL where SQL_TEXT like :marker',marker='/* '+marker+' */%')
    names=[c[0].lower() for c in cur.description]
    report['cursors']=[dict(zip(names,row)) for row in cur]
    for item in report['cursors']:
        try:
            cur.execute("select PLAN_TABLE_OUTPUT from table(DBMS_XPLAN.DISPLAY_CURSOR(:sid,:child,'ALLSTATS LAST +PREDICATE +ALIAS'))",
                        sid=item['sql_id'],child=item['child_number'])
            item['runtime_plan']=[row[0] for row in cur]
            if any('privilege' in line.lower() for line in item['runtime_plan']):
                cur.execute('select ID,PARENT_ID,OPERATION,OPTIONS,OBJECT_NAME,CARDINALITY,COST,ACCESS_PREDICATES,FILTER_PREDICATES '
                            'from V$SQL_PLAN where SQL_ID=:sid and CHILD_NUMBER=:child order by ID',
                            sid=item['sql_id'],child=item['child_number'])
                columns=[c[0].lower() for c in cur.description]
                item['cursor_plan']=[dict(zip(columns,row)) for row in cur]
        except Exception as exc:
            item['plan_error']=str(exc)
    connection.rollback()
report['status']='CAPTURED' if report['cursors'] else 'CURSOR_NOT_FOUND'
target=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T12/available-sts-runtime-plan.json'
target.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps({k:report[k]for k in ('status','ms','rows')}))
for item in report['cursors']:
    print(json.dumps({k:v for k,v in item.items()if k not in ('runtime_plan','cursor_plan')}))
    print('\n'.join(item.get('runtime_plan',[])[:95]))
    for node in item.get('cursor_plan',[]):
        print(json.dumps(node))
