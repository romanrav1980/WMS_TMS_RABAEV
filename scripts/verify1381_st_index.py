exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,sql in [('index',"select INDEX_NAME,STATUS,VISIBILITY from USER_INDEXES where INDEX_NAME='RRL_ST_PAGE_KEYS_I'"),('migration',"select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-14-1381-st-page-keys'"),('invalid',"select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%'"),('columns',"select COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where INDEX_NAME='RRL_ST_PAGE_KEYS_I' order by COLUMN_POSITION")]:
  q.execute(sql);result[name]=q.fetchall()
assert result['index']==[('RRL_ST_PAGE_KEYS_I','VALID','VISIBLE')]
assert result['migration'][0][1]=='APPLIED'
print(json.dumps(result));Path('tmp/verify1381.json').write_text(json.dumps(result,indent=2),encoding='utf-8')