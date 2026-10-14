exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 for name,sql in [('object',"select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where OBJECT_NAME='RRL_ADDR'"),('synonym',"select TABLE_OWNER,TABLE_NAME from USER_SYNONYMS where SYNONYM_NAME='RRL_ADDR'"),('indexes',"select i.INDEX_NAME,i.UNIQUENESS,i.STATUS,c.COLUMN_NAME,c.COLUMN_POSITION from USER_INDEXES i join USER_IND_COLUMNS c on c.INDEX_NAME=i.INDEX_NAME where i.TABLE_NAME='RRL_ADDR' order by i.INDEX_NAME,c.COLUMN_POSITION"),('duplicate',"select ADDR,count(*) from RRL_ADDR group by ADDR having count(*)>1 fetch first 1 rows only")]:
  q.execute(sql);print(name,json.dumps(q.fetchall()))
