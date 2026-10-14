exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib
folder=Path('db/migrations/2026-10-14_ni022_vehicle_outer_dimensions');folder.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");target=q.fetchone();assert target==('RABAEV','orcl')
 q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY','RRL_VEHICLE_PROFILE_API',user)from dual");body=q.fetchone()[0].read().strip()+'\n/\n';(folder/'000_before_body.sql').write_text(body,encoding='utf-8')
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");invalid=q.fetchall()
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_VEHICLE_PROFILE_HIST'and COLUMN_NAME like 'OUTER_%'");columns=q.fetchall()
(folder/'000_checkpoint.json').write_text(json.dumps({'target':target,'before_body_sha256':hashlib.sha256(body.encode()).hexdigest(),'invalid':invalid,'outer_columns':columns},indent=2),encoding='utf-8');print('checkpoint captured; invalid',invalid,'outer existing',columns)
