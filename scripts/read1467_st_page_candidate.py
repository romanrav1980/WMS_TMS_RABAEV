exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.transport.infrastructure.available_sts_query import available_sts_query
import time
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=20000;q=c.cursor();sql,binds=available_sts_query(unassigned_only=False,page=1,page_size=200);results=[];baseline=None
 for name,query in [('existing',sql),('nested',sql.replace('SELECT P.ST_NUMBER','SELECT /*+ leading(K P R A) use_nl(P R A) index(P RRL_ST_PAGE_KEYS_I) */ P.ST_NUMBER',1))]:
  start=time.perf_counter();q.execute(query,binds);rows=q.fetchall();elapsed=time.perf_counter()-start
  if baseline is None:baseline=rows
  else:assert rows==baseline
  results.append({'variant':name,'seconds':elapsed,'rows':len(rows),'equal':True})
 print(json.dumps(results));Path('tmp/result1467.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
