exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_HU_CMD","RRL_STOCK_TRANSFER_CORE","RRL_STOCK_LOCATION_CORE"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='PACKAGE BODY'order by LINE",pkg=name)
  body="".join(r[0]for r in q).replace(chr(13)," ").strip();Path("tmp/317_"+name.lower()+"_body.sql").write_text(body,encoding="utf-8")
