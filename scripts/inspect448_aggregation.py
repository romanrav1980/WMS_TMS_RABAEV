exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select text from user_source where name='RRL_REGULATORY_API'and type='PACKAGE'order by line")
 print("SPEC", "".join(r[0]for r in q))
 q.execute("select column_name,data_type from user_tab_columns where table_name='RRL_CRPT_AGGREGATION'order by column_id")
 print("COLS",q.fetchall())
 q.execute("select object_name,object_type from user_objects where object_name like '%TRACE%AGG%'or object_name like '%REGULATORY%'")
 print("OBJECTS",q.fetchall())
