exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib
folder=Path('db/migrations/2026-10-14_ni022_vehicle_outer_dimensions')
expected=json.loads((folder/'000_checkpoint.json').read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert list(q.fetchone())==expected['target']
 q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY','RRL_VEHICLE_PROFILE_API',user) from dual")
 body=q.fetchone()[0].read().strip()+'\n/\n'
 assert hashlib.sha256(body.encode()).hexdigest()==expected['before_body_sha256'],'Owner changed since checkpoint'
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.sql')}
(folder/'reviewed_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('PASS current owner matches checkpoint; reviewed SQL manifest saved')
