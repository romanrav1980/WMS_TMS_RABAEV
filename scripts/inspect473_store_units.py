exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STORE_RECEIPT_UNIT","RRL_STORE_RETURN_APPROVAL"]:
  q.execute("select column_name from user_tab_columns where table_name=:n order by column_id",n=name);print(name,q.fetchall())
 q.execute("select UNIT_DISPOSITION,PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:op",op=json.loads(Path("tmp/context383.json").read_text(encoding="utf-8"))["body"]["operation_id"]);print(q.fetchall())
