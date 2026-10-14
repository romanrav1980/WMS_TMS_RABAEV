from pathlib import Path
import json,hashlib
exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
p=Path('db/migrations/2026-10-14_ni081_store_weekly_windows');p.mkdir(exist_ok=True)
manifest={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for name in ['RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API']:
  for typ in ['PACKAGE','PACKAGE BODY']:
   q.execute('select text from user_source where name=:n and type=:t order by line',n=name,t=typ)
   src=''.join(r[0] for r in q).replace('\r\n','\n')
   assert src,name
   f='000_before_'+name.lower()+'_'+typ.lower().replace(' ','_')+'.sql'
   text='create or replace '+src+'\n/\n';(p/f).write_text(text,encoding='utf-8');manifest[f]=hashlib.sha256(text.encode()).hexdigest()
 q.execute("select sys_context('USERENV','SESSION_USER'),sys_context('USERENV','SERVICE_NAME') from dual")
 manifest['target']=q.fetchone()
(p/'000_checkpoint.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(manifest['target'])

