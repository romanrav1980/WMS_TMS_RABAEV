exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from time import perf_counter
fixture=json.loads(Path('reports/retailcase/2026-10-13/codex/STORE_ACCESS/native.json').read_text());results=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for sqlid,bind in [('7bk76xyqrjdsw',json.dumps([fixture['st_number']])),('3u00sw0qctbxs',json.dumps([fixture['st_id']]))]:
  q.execute('select SQL_FULLTEXT from V$SQL where SQL_ID=:id fetch first 1 row only',id=sqlid);old=q.fetchone()[0].read();new=old.replace('SELECT ', 'SELECT /*+ leading(inputs) use_nl(p) index(p) */ ',1)
  row={'source_sql_id':sqlid};previous=None
  for label,query in [('old',old),('indexed',new)]:
   started=perf_counter();q.execute(query,{'B1':bind});data=q.fetchall();row[label+'_ms']=round((perf_counter()-started)*1000,3)
   if previous is not None:assert data==previous
   previous=data
  results.append(row)
Path('reports/retailcase/2026-10-13/codex/STORE_ACCESS/lookup_comparison.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(results)
