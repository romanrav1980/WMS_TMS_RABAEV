exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,DEFAULT_RECEIVE_CELL from RRL_WARES where ID=9807");print("DEFAULT",q.fetchall())
 q.execute("select CELL,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS from RRL_CELLS where WARE_ID=9807 order by CELL fetch first 12 rows only");print("CELLS",json.dumps(q.fetchall(),ensure_ascii=True))
