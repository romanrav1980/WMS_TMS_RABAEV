exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));probe=json.loads(Path("tmp/context753.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=ctx["dst"]);assert q.fetchone()==(3,3)
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:task",task=probe["task"]);assert q.fetchone()==("CANCELLED",)
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op",op="PROBE753:"+ctx["tag"]);assert q.fetchone()==(0,)
print("PASS758 waiting probe has no committed stock command; existing cancel preserved original P3H3; typed domain handler extension required")
