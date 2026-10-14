exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni053_partial_final_receipt");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,kind in[("RRL_STOCK_UNIT_GUARD","TRIGGER"),("RRL_STOCK_STORE_RECEIPT_READ","PACKAGE BODY"),("RRL_STOCK_STORE_RECEIPT_CMD","PACKAGE BODY")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind);source="".join(r[0]for r in q).replace(chr(13)," ").strip();assert source
  (d/("000_before_"+name.lower()+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
print("Captured297 current stockunit guard +existing final recipient read/command; no mutation")
