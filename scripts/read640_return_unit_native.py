exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_UNIT_CORE'and TYPE='PACKAGE BODY'order by LINE")
 text="".join(r[0]for r in q);i=text.find("procedure receive_return(");j=text.find("\n end;",i)
 print(text[i:j+6])
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_WMS_HU_LINK'and COLUMN_NAME in('CHILD_PALLET_UID','PARENT_UID','ACTIVE_FLAG')");print(q.fetchall())
