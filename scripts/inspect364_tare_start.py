exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TARE_PLANNING'and TYPE='PACKAGE BODY'order by LINE")
 print("".join(x[0]for x in q)[:3800])
 q.execute("select CASE_PICK_TASK_ID,PALLET_TYPE_ID,STARTED_AT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(1031,1112)");print(json.dumps(q.fetchall(),default=str))
