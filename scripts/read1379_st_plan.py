exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.transport.infrastructure.available_sts_query import available_sts_query
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=10000;q=c.cursor();sql,params=available_sts_query(unassigned_only=False,page_size=200)
 q.execute("explain plan set statement_id='NICORA1379' for "+sql,params)
 q.execute("select PLAN_TABLE_OUTPUT from table(DBMS_XPLAN.DISPLAY(null,'NICORA1379','TYPICAL'))")
 print('\n'.join(r[0]for r in q));c.rollback()