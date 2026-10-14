exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-12_ni061_recovery_consolidation");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,typ,file in [("RRL_STOCK_IW_RECOVERY_NEXT","PACKAGE BODY","000_before_next.sql"),("RRL_STOCK_HU_SHIP_CMD","PACKAGE BODY","000_before_ship.sql")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:typ order by LINE",name=name,typ=typ)
  text="create or replace "+"".join(x[0]for x in q).replace("\r","").strip()+"\n/\n";(d/file).write_text(text,encoding="utf-8")
 q.execute("select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_IW_RECOVERY_DISPATCH'and CONSTRAINT_TYPE='P'");print(q.fetchall())
 for old,new in [("source305_marked_case.py","source368_marked_case.py"),("receive305_initial.py","receive368_initial.py"),("case305_partial_recovery.py","case368_partial_recovery.py")]:
  Path("scripts/"+new).write_text(Path("scripts/"+old).read_text(encoding="utf-8").replace("305","368"),encoding="utf-8")
 Path("scripts/place371.py").write_text(Path("scripts/place306.py").read_text(encoding="utf-8").replace("305","368").replace("306","371"),encoding="utf-8")
