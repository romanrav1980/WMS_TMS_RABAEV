exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib,datetime
folder=Path('db/migrations/2026-10-14_ni022_store_access_dimensions')
folder.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor()
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 target=q.fetchone()
 if target[0]!='RABAEV' or target[1].lower()!='orcl':raise RuntimeError('Unexpected target')
 manifest={'migration_id':'2026-10-14-ni022-store-access-dimensions','target':target,'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{}}
 for kind in ['PACKAGE','PACKAGE BODY']:
  q.execute('select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE',name='RRL_TRANSPORT_PLAN_RULES',kind=kind)
  source=''.join(r[0] for r in q)
  if not source:raise RuntimeError('Missing native source')
  path=folder/('000_before_rules_'+kind.lower().replace(' ','_')+'.sql')
  path.write_text('create or replace '+source+'\n/\n',encoding='utf-8')
  manifest['files'][path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%' order by 1,2")
 manifest['invalid_before']=q.fetchall()
 (folder/'000_checkpoint.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(json.dumps({'target':target,'checkpoint_files':len(manifest['files']),'invalid_before':len(manifest['invalid_before'])}))
