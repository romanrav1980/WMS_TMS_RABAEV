from pathlib import Path
s=Path('scripts/read1376_st_page.py').read_text(encoding='utf-8').replace("tmp/result1376.json","tmp/result1481.json")
s=s.replace("with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:\n q=c.cursor();q.execute(\"\"\"select SQL_ID", "with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:\n q=c.cursor();q.execute(\"select STATUS,VALIDATED from USER_CONSTRAINTS where TABLE_NAME='RRL_ADDR' and CONSTRAINT_TYPE='P'\");result['addr_pk']=q.fetchall();q.execute(\"\"\"select SQL_ID")
Path('scripts/read1481_st_http.py').write_text(s,encoding='utf-8')
