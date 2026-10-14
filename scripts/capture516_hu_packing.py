exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=Path("tmp/packing516");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STOCK_HU_CMD","RRL_STOCK_HU_READ","RRL_HU_REPACK_API"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='PACKAGE BODY'order by LINE",name=name)
  src="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
  assert len(src)>100
  (d/(name+".sql")).write_text(src,encoding="utf-8")
  print(name,len(src),src.count("insert into RRL_WMS_HU_LINK"))
