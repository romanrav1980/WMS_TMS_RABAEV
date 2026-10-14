exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,CONDITION,PAY_ORDER_ID,DELETED from RRL_TRANSPORT_TASK where ID=33571");print(json.dumps(q.fetchone()))
