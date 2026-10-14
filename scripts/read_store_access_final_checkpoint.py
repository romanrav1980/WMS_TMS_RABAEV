exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib
folder=Path('db/migrations/2026-10-14_ni022_store_access_dimensions');manifest=json.loads((folder/'000_checkpoint.json').read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ['RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD']:
  q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY',:n,user)from dual",n=name);body=q.fetchone()[0].read().strip()+'\n/\n';filename='000_before_'+name.lower()+'.sql';(folder/filename).write_text(body,encoding='utf-8');manifest[filename]=hashlib.sha256(body.encode()).hexdigest()
(folder/'000_checkpoint.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
