exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib
folder=Path('db/migrations/2026-10-14_ni022_store_access_dimensions')
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==('RABAEV','orcl')
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_RULES' and TYPE='PACKAGE BODY' order by LINE")
 live='create or replace '+''.join(r[0] for r in q)+'\n/\n'
 assert [x for x in live.splitlines() if x.strip()]==[x for x in (folder/'000_before_rules_package_body.sql').read_text(encoding='utf-8').splitlines() if x.strip()],'Plan owner drift'
 for name in ['RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD']:
  q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY',:name,user) from dual",name=name)
  live=q.fetchone()[0].read().strip()
  saved=(folder/('000_before_'+name.lower()+'.sql')).read_text(encoding='utf-8').strip()
  assert saved.removesuffix('/').strip()==live,name+' drift'
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.sql')}
(folder/'reviewed_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('PASS three current native owners match saved checkpoint; reviewed manifest saved')

