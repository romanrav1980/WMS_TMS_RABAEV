exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RESULT_JSON from RRL_WORKLOAD_OPERATION where ROWNUM<=2")
 for row in q:
  value=row[0];data=value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,'read')else value);print(json.dumps(data,ensure_ascii=True))