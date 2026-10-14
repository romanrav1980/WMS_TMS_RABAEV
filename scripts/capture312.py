exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
folder=Path("db/migrations/2026-10-12_ni061_nested_onward");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,kind in [("RRL_STOCK_HU_SHIP_CMD","PACKAGE BODY"),("RRL_STOCK_INTERWARE_NEXT","PACKAGE BODY"),("RRL_STOCK_IW_RECOVERY_NEXT","PACKAGE BODY"),("RRL_INTERWARE_ONWARD_FACT_GUARD","TRIGGER"),("RRL_IW_REC_DISPATCH_GUARD","TRIGGER")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind)
  body="".join(r[0]for r in q).replace(chr(13)," ").strip();assert body,name
  out[(folder/("000_before_"+name.lower()+".sql")).as_posix()]="create or replace "+body+"\n/\n"
print(json.dumps(out))
