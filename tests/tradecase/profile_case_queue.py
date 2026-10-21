"""Compare the exact CASE list and candidate rewrites in one Oracle READ ONLY snapshot."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
from time import perf_counter
from uuid import uuid4
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'api/wms_api_server')]
from app.modules.resources.infrastructure.case_read_model import LegacyCaseReads
from app.modules.resources.infrastructure import case_read_model
from app.modules.resources.infrastructure.case_view_scope import require_viewer
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T12';OUT.mkdir(parents=True,exist_ok=True)
report=dict(status='FAIL',cases=[],isolation='ONE_ORACLE_READ_ONLY_SNAPSHOT',physical_writes=0)


class Capture:
    def fetch_all(self,sql,params):self.sql,self.params=sql,params;return []


def fingerprint(rows):return sha256(json.dumps(rows,default=str,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()


def capture_query(resource=None,scope='all',status=None,limit=200,warehouse=None,actor='admin',before=False):
    result=Capture()
    template=(OUT/'case-queue-before-template.sql').read_text(encoding='utf-8') if before else case_read_model.CASE_TASK_LIST_SQL
    with patch.object(case_read_model,'CASE_TASK_LIST_SQL',template):
        LegacyCaseReads(result).list_tasks(resource,scope,status,limit,warehouse,view_actor=actor)
    return result


if __name__=='__main__':
    try:
        with oracle_connection()as conn:
            q=conn.cursor();q.execute('set transaction read only')
            q.execute("select user,sys_context('USERENV','SERVICE_NAME'),sys_context('USERENV','SID')from dual");identity=q.fetchone();assert identity[:2]==('RABAEV','orcl');report['identity']=list(identity)
            q.execute('select count(*)from RRL_CASE_PICK_TASK');report['total_case_tasks']=q.fetchone()[0]
            for warehouse in [None,219023232,220639789]:
                began=perf_counter();require_viewer(q,'admin',warehouse);admission_ms=(perf_counter()-began)*1000
                capture=capture_query(warehouse=warehouse,before=True)
                production=capture_query(warehouse=warehouse)
                base=capture.sql
                # The final projection joins the already authorized selected IDs in the same snapshot.
                marker='                 where '
                left,where=base.rsplit(marker,1);projection_only=left+where[where.index('\n'):]
                materialized=base.replace('select CASE_PICK_TASK_ID,PICK_WAVE_ID from (','select /*+ materialize */ CASE_PICK_TASK_ID,PICK_WAVE_ID from (',1)
                both=projection_only.replace('select CASE_PICK_TASK_ID,PICK_WAVE_ID from (','select /*+ materialize */ CASE_PICK_TASK_ID,PICK_WAVE_ID from (',1)
                variants=dict(base=(base,100),materialized=(materialized,100),projection_only=(projection_only,100),both=(both,100),base_fetch500=(base,500),production=(production.sql,100))
                samples=defaultdict(list);expected=None;tag=uuid4().hex[:8];last=[]
                for round_no in range(6):
                    names=list(variants);names=names[round_no%len(names):]+names[:round_no%len(names)]
                    for name in names:
                        sql,arraysize=variants[name]
                        with conn.cursor()as cursor:
                            cursor.arraysize=arraysize;cursor.prefetchrows=2
                            began=perf_counter();cursor.execute('/* TC22.CASE.'+tag+'.'+name+' */ '+sql,capture.params);executed=perf_counter();rows=cursor.fetchall();ended=perf_counter()
                            sig=fingerprint(rows)
                            if expected is None:expected=sig;last=rows
                            assert sig==expected,(warehouse,name,'RESULT_DIFFERENCE')
                            samples[name].append(dict(total_ms=round((ended-began)*1000,3),execute_ms=round((executed-began)*1000,3),fetch_ms=round((ended-executed)*1000,3),rows=len(rows),sha=sig,warmup=round_no==0))
                item=dict(warehouse=warehouse,limit=200,scope='all',admission_ms=round(admission_ms,3),rows=len(last),sha=expected,samples=samples,
                          medians={n:round(statistics.median(x['total_ms']for x in s[1:]),3)for n,s in samples.items()},plans={})
                report['cases'].append(item)
                for name in variants:
                    q.execute("select SQL_ID,CHILD_NUMBER,PLAN_HASH_VALUE from v$sql where SQL_TEXT like :prefix and PARSING_SCHEMA_NAME=user",prefix='/* TC22.CASE.'+tag+'.'+name+' */%')
                    for sql_id,child,plan in q.fetchall():
                        try:
                            q.execute("select PLAN_TABLE_OUTPUT from table(dbms_xplan.display_cursor(:id,:child,'TYPICAL'))",id=sql_id,child=child)
                            item['plans'][name]=dict(sql_id=sql_id,child=child,plan_hash=plan,text='\n'.join(x[0]for x in q))
                        except oracledb.DatabaseError as exc:item['plans'][name]=dict(sql_id=sql_id,plan_hash=plan,error=str(exc))
                (OUT/'case-queue-profile.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
            report['status']='PASS'
    except Exception as exc:report['error']=str(exc);raise
    finally:(OUT/'case-queue-profile.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps({**{k:v for k,v in report.items()if k!='cases'},'cases':[{k:v for k,v in x.items()if k not in ['samples','plans']}for x in report['cases']]}))
