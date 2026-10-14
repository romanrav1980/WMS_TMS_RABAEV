exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.reconciliation_documents import daily_counts,backlog_documents
from app.modules.finance.infrastructure.reconciliation_sources import DAILY,BACKLOG
from datetime import datetime,timezone
import time
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor();q.execute('set transaction read only')
 for ware in [9807,6667491]:
  expected={}
  for key,sql in BACKLOG:q.execute(sql,ware=ware);expected[key]=int(q.fetchone()[0])
  t=time.perf_counter();actual,details=backlog_documents(q,ware);elapsed=time.perf_counter()-t
  assert actual==expected,(actual,expected)
  assert all(len(d['document_ids'])==min(actual[k],20) and d['has_more']==(actual[k]>20)for k,d in details.items())
  result[str(ware)]={'counts':actual,'seconds':round(elapsed,3),'documents':details}
 params={'ware':9807,'day_from':datetime(2026,10,14,tzinfo=timezone.utc),'day_to':datetime(2026,10,15,tzinfo=timezone.utc)};expected={}
 for key,sql in DAILY:q.execute(sql,params);expected[key]=int(q.fetchone()[0])
 assert daily_counts(q,params)==expected
 result['daily_equal']=True
print(json.dumps({w:{k:v for k,v in r.items()if k!='documents'}if isinstance(r,dict)else r for w,r in result.items()}));Path('tmp/result1392.json').write_text(json.dumps(result,indent=2),encoding='utf-8')