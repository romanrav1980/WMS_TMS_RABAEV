import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni062_return_basis")
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select text from user_source where name='RRL_STOCK_STORE_RETURN_SAP_CMD'and type='PACKAGE BODY'order by line")
 native="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
print(json.dumps({str(d/"000_before_rrl_stock_store_return_sap_cmd_package_body.sql"):native}))
