exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,substr(SQL_TEXT,1,600)from V$SQL where SQL_ID in('9s2z9dtc37cs8','f3br1qjfgwzv0')")
 print(json.dumps(q.fetchall()))
 q.execute("select PLAN_TABLE_OUTPUT from table(dbms_xplan.display_cursor('f3br1qjfgwzv0',null,'BASIC'))")
 print(json.dumps([r[0]for r in q.fetchall()][:24]))
