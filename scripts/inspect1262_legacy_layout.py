exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in("RRL_UPDATE_SBORKA_PALLET_ROWS2","RRL_SBORKA_PALLET_ROWS_ADD4"):
  q.execute("select TEXT from USER_SOURCE where NAME=:name order by LINE",name=name)
  body="".join(x[0]for x in q).replace("\r","");Path("tmp/"+name.lower()+"1262.sql").write_text(body,encoding="utf-8")
  print(body[:17000])
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_SBORKA_PALLET_ROWS'and STATUS='ENABLED'");print(json.dumps({"triggers":q.fetchall()}))
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLET_ROWS' order by COLUMN_ID");print(json.dumps({"columns":q.fetchall()}))
