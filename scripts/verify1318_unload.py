exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STORE_UNLOAD_CORE'");errors=q.fetchall();print(json.dumps(errors));assert not errors
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'");invalid=q.fetchall();print(json.dumps(invalid));assert not invalid
