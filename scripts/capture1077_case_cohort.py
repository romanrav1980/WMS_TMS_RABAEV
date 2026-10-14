exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_CASE_WAIT'and TYPE='PACKAGE BODY'order by LINE")
 t="".join(x[0]for x in q)
 Path("tmp/1077_rrl_st_defer_case_wait_package_body.sql").write_text("create or replace "+t+"\n/\n",encoding="utf-8",newline="\n")
 q.execute("select p.TASK_ID,p.BASE_UOM from RRL_ST_DEFER_WAIT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where t.STATUS not in('DONE','CANCELLED')")
 print("Current open waiting plans",q.fetchall())
