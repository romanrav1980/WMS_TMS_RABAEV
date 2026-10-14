exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_recovery_placement");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_TASK_PLAN","RRL_STOCK_TASK_CORE","RRL_STOCK_TASK_DOMAIN"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='PACKAGE BODY'order by LINE",pkg=name)
  source="".join(r[0]for r in q).replace(chr(13)," ").strip();assert source
  (d/("000_before_"+name.lower()+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
print("Captured301 current native task plan/core/domain sources only")
