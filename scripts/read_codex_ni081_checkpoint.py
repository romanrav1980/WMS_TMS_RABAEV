exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
folder=Path('db/migrations/2026-10-14_ni081_route_rest_approval');folder.mkdir(exist_ok=True)
manifest={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ['RRL_TT_TIME_API','RRL_TT_ROUTE_API']:
  for kind in ['PACKAGE','PACKAGE_BODY']:
   q.execute("select dbms_metadata.get_ddl(:kind,:name,user)from dual",kind=kind,name=name);raw=q.fetchone()[0].read().replace('\r\n','\n').replace('\r','\n').strip()+'\n/\n';file='000_before_'+name.lower()+'_'+kind.lower()+'.sql';(folder/file).write_text(raw,encoding='utf-8');manifest[file]=hashlib.sha256(raw.encode()).hexdigest()
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%' order by 1,2");manifest['invalid_before']=q.fetchall()
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_TIME_APPROVAL' order by COLUMN_ID");manifest['approval_columns']=q.fetchall()
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_ADDR_DISTANCE_MATRIX'");manifest['road_triggers']=q.fetchall()
(folder/'000_checkpoint.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest))