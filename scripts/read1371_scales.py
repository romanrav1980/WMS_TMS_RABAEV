exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select RESULT_JSON from RRL_WH_SCALE_CAPTURE where CAPTURE_PURPOSE='PICK' order by RECEIVED_AT desc fetch first 2 rows only")
 for row in q:
  value=row[0];print(json.dumps(value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,"read")else value),default=str))
