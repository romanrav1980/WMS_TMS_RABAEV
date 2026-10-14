exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.delivery.infrastructure.return_progress import return_progress
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 print(return_progress(q,["REUSE643.APPROVE:dc1889623c"],"admin"))
