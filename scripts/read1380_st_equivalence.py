exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.transport.infrastructure.available_sts_query import available_sts_query
from app.modules.transport.infrastructure.available_sts_page import _window
import time
saved=json.loads(Path('tmp/files1375.json').read_text(encoding='utf-16'))
ns={'__file__':str(Path('api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.py').resolve())}
exec(saved['api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.py'],ns)
ns['QUERY']=saved['api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.sql']
result=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=60000;q=c.cursor()
 for filters in [dict(unassigned_only=False),dict(unassigned_only=False,ware_id=9807),dict(ware_id=9807,assembled_only=True),dict(ware_id=9807,not_assembled_only=True,max_weight_kg=1000)]:
  sql,params=ns['available_sts_query'](**filters);params.update(page_end=200,page_offset=0);sql=_window(sql);t=time.perf_counter();q.execute(sql,params);before=[r[:-1] for r in q.fetchall()];oldtime=time.perf_counter()-t
  sql,params=available_sts_query(**filters,page=1,page_size=200);t=time.perf_counter();q.execute(sql,params);after=q.fetchall();after=[r[:-1] for r in after] if q.description[-1][0]=='PAGE_ROW_NUMBER' else after;newtime=time.perf_counter()-t
  assert before==after, 'Mismatch '+str(filters)
  result.append({'filters':filters,'rows':len(after),'old_seconds':round(oldtime,3),'new_seconds':round(newtime,3)})
print(json.dumps(result));Path('tmp/result1380.json').write_text(json.dumps(result,indent=2),encoding='utf-8')