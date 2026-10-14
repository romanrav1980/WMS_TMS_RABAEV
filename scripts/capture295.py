exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_shortage_disposition");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for pkg in["RRL_STOCK_POSTING_API","RRL_INTERWARE_UNIT_SOURCE","RRL_STOCK_INTERWARE_CUSTODY","RRL_STOCK_INTERWARE_NEXT","RRL_INTERWARE_DEPART_GATE"]:
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=pkg,kind=kind)
   lines="".join(r[0]for r in q);assert lines
   (d/("000_before_"+pkg.lower()+"_"+kind.lower().replace(" ","_")+".sql")).write_text("create or replace "+lines.replace(chr(13)," ").strip()+"\n/\n",encoding="utf-8")
print("Captured295 exact five current native sources; no DB copy/no mutation")
