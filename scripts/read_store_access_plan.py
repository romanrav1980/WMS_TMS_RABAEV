exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLETS'and COLUMN_NAME in('ID','ST_NUMBER')order by INDEX_NAME,COLUMN_POSITION");print(q.fetchall())
 for sqlid in ['7bk76xyqrjdsw','3u00sw0qctbxs']:
  q.execute("select PLAN_TABLE_OUTPUT from table(dbms_xplan.display_cursor(:sqlid,null,'BASIC'))",sqlid=sqlid);print(sqlid,'\n'.join(x[0]for x in q.fetchall()))
