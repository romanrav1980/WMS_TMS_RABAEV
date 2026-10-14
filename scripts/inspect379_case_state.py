exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context376.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS,CONTENT_VERSION,SHIPPED_OPERATION,WARE_ID,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ctx["case"]);print(q.fetchall())
 q.execute("select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:id",id=ctx["case"]);print(q.fetchall())
