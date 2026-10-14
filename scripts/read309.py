exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import re
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ["RRL_STOCK_HU_READ","RRL_STOCK_UNLOAD_CMD"]:
 sources=[path for path in m["components"]if re.search(r"create\s+or\s+replace\s+package\s+"+name+r"\s",(p.parent/path).read_text(encoding="utf-8"),re.I)]
 print(name,sources)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STOCK_HU_READ","RRL_STOCK_UNLOAD_CMD"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='PACKAGE BODY'order by LINE",pkg=name)
  source="".join(r[0]for r in q).replace(chr(13)," ").strip()
  Path("tmp/309_"+name.lower()+".sql").write_text(source,encoding="utf-8")
print("Captured309 readonly current HU guard/unload owner")
