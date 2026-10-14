exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_ST_DEFER_WAIT_PLAN','RRL_ST_DEFER_WAIT_RUN')")
 for (n,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n order by LINE",n=n);print(n,"".join(r[0]for r in q))
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_SHIPMENT_CMD'and TYPE='PACKAGE BODY'order by LINE")
 body="".join(r[0]for r in q);Path("tmp/952_case_shipment.sql").write_text(body,encoding="utf-8")
 q.execute("select CASE_PICK_TASK_ID,STATUS,CURRENT_CELL,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID is not null and STATUS in('WAIT_CONTROL','CONTROLLED','READY_TO_SHIP')fetch first 8 rows only");print("CANDIDATES",q.fetchall())
