"""Compare existing any-warehouse precheck with current-warehouse-first check; no cached permissions."""
import json
from pathlib import Path
import secrets
import statistics
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection

TAG='TS23'+uuid4().hex[:10]
WARE=220793322
report=dict(status='FAIL',samples=[],warehouse=WARE)
created=False
OLD="""select count(*)from RUSERS where ID=:a and nvl(DELETED,0)=0 and
 (RRL_ACCESS_API.is_admin(:a)=1 or exists(select 1 from RRL_WARES rw
 where RRL_ACCESS_API.allowed(:a,'transport_dispatch_view','WAREHOUSE',to_char(rw.ID))=1))"""
NEW="""select case when RRL_ACCESS_API.is_admin(:a)=1 then 1
 when RRL_ACCESS_API.allowed(:a,'transport_dispatch_view','WAREHOUSE',to_char(WARE_ID))=1 then 1
 when exists(select 1 from RRL_WARES rw where RRL_ACCESS_API.allowed(:a,'transport_dispatch_view','WAREHOUSE',to_char(rw.ID))=1)then 1 else 0 end
 from RUSERS where ID=:a and nvl(DELETED,0)=0"""
try:
    with oracle_connection()as c:
        q=c.cursor()
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Transport scope QA','TC03QA',:w,0,1)",a=TAG,p=secrets.token_hex(24),w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Transport scope QA',1,1)",a=TAG)
        q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'transport_dispatch_view')",a=TAG)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Transport scope benchmark',1)",a=TAG,w=str(WARE))
        c.commit();created=True
        q.execute('select count(*)from RRL_WARES');report['warehouse_rows']=q.fetchone()[0]
        for i in range(6):
            row={}
            for name,sql in [('old',OLD),('new',NEW)]:
                start=time.perf_counter();q.execute(sql,a=TAG);assert q.fetchone()==(1,)
                row[name]=round((time.perf_counter()-start)*1000,2)
            report['samples'].append(row)
        report['warm_medians']={k:statistics.median(r[k]for r in report['samples'][1:])for k in ('old','new')}
        q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=TAG);c.commit()
        for sql in (OLD,NEW):q.execute(sql,a=TAG);assert q.fetchone()==(0,)
        report.update(status='PASS',revocation_equal=True)
finally:
    if created:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=TAG);c.commit()
        report['qa_retired']=True
    path=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T09'/f'{TAG}.json'
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
