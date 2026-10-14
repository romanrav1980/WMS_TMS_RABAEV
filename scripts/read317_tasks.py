exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_HU_TASK","RRL_STOCK_INTERWARE_PUT"]:
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind)
   body="".join(r[0]for r in q).replace(chr(13)," ").strip()
   Path("tmp/317_"+name.lower()+"_"+kind.replace(" ","_").lower()+".sql").write_text(body,encoding="utf-8")
   print(name,kind,len(body))
