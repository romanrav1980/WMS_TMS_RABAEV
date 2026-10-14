exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000
 try:
  q=c.cursor();print(q.callfunc("RRL_PICK_PLAN_CREATE_API.create_command",oracledb.DB_TYPE_NUMBER,["PICK.DIAG.1234",2135,"FEFO","admin"]))
 finally:c.rollback()
