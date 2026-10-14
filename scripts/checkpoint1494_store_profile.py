exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib,datetime
folder=Path('db/migrations/2026-10-14_ni051_store_profile')
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");target=q.fetchone();assert target==('RABAEV','orcl')
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_PROFILE','RRL_STORE_RECEIVING_WINDOW','RRL_STORE_PROFILE_CHANGE','RRL_STORE_PROFILE_GUARD','RRL_STORE_RECEIVING_WINDOW_GUARD','RRL_STORE_PROFILE_CHANGE_GUARD')")
 objects=q.fetchall();assert not objects,'Unexpected existing profile objects; inspect drift'
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%'");invalid=q.fetchall()
 manifest={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':target,'existing_objects':objects,'invalid_before':invalid,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.sql')}}
 (folder/'000_checkpoint.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print('PASS profile objects absent; SQL checkpoint saved; invalid',len(invalid))
