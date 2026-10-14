exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.transport.infrastructure.available_sts_query import available_sts_query
import app.modules.transport.infrastructure.available_sts_query as query_module
import time
old={};exec(Path('tmp/available_sts_page_before1477.py').read_text(encoding='utf-8'),old)
new=query_module.page_available_sts;results=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=20000;q=c.cursor()
 for filters in [dict(unassigned_only=False,page=1,page_size=200),dict(unassigned_only=False,page=2,page_size=200),dict(unassigned_only=False,ware_id=9807,page_size=2),dict(ware_id=9807,not_assembled_only=True,max_weight_kg=1000,page_size=2)]:
  baseline=None;timings={}
  for name,builder in [('old',old['page_available_sts']),('new',new)]:
   query_module.page_available_sts=builder;sql,binds=available_sts_query(**filters);start=time.perf_counter();q.execute(sql,binds);rows=q.fetchall();timings[name]=round(time.perf_counter()-start,3)
   if baseline is None:baseline=rows
   else:assert rows==baseline,filters
  results.append({'filters':filters,'rows':len(rows),'seconds':timings,'equal':True})
 query_module.page_available_sts=new
 print(json.dumps(results));Path('tmp/result1478.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
