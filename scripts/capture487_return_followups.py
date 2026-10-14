import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
out={};d=Path("db/migrations/2026-10-12_ni062_return_basis")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STOCK_STORE_RETURN_REC_CMD","RRL_STOCK_STORE_RETURN_TR_CMD","RRL_STOCK_STORE_RETURN_CUST_CMD","RRL_RETURN_REUSE_API"]:
  q.execute("select text from user_source where name=:n and type='PACKAGE BODY'order by line",n=name)
  src="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
  out[str(d/("000_before_"+name.lower()+"_package_body.sql"))]=src
print(json.dumps(out))
