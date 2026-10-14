exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in("RRL_UPDATE_PALLET_ROW2","RRL_QC_ROWS_INVALIDATE","RRL_QC_ROWS_INSERT"):
  q.execute("select TEXT from USER_SOURCE where NAME=:name order by LINE",name=name);body="".join(x[0]for x in q).replace("\r","")
  Path("tmp/"+name.lower()+"1263.sql").write_text(body,encoding="utf-8");print(body[:18000])
