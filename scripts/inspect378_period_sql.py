exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context376.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for expr in ["trunc(cast(t.STARTED_AT_INSTANT at time zone(:zone)as timestamp))","to_date(to_char(t.STARTED_AT_INSTANT at time zone(:zone),'YYYY-MM-DD'),'FXYYYY-MM-DD')"]:
  sql="select count(*),min("+expr+")from RRL_TT_LOAD_BOX_WEIGHT b join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID where b.LOAD_OPERATION_ID=:op"
  try:q.execute(sql,zone="Pacific/Kiritimati",op=ctx["load_operation_id"]);print(expr,q.fetchall())
  except oracledb.DatabaseError as e:print(str(e))
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_LOG_COST_LINE_GUARD'and LINE between 16 and 22 order by LINE");print(q.fetchall())
