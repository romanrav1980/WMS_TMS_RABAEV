exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import time
case=json.loads(Path("tmp/browser1236.json").read_text());op=case["replay"]["operation_id"];pid=case["replay"]["pick_plan_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_PICK_PLAN_CREATE_API','RRL_PICK_CREATE_OP_GUARD','RRL_PICKING_API','RRL_PICK_PLAN_ADMISSION')")
 errors=q.fetchall();assert not errors,errors
 start=time.perf_counter();replay=q.callfunc("RRL_PICK_PLAN_CREATE_API.create_command",oracledb.DB_TYPE_NUMBER,[op,2135,"FEFO","admin"]);elapsed=round((time.perf_counter()-start)*1000,3);assert replay==pid
 try:q.callfunc("RRL_PICK_PLAN_CREATE_API.create_command",oracledb.DB_TYPE_NUMBER,[op,2135,"FIFO","admin"])
 except oracledb.Error as e:
  assert e.args[0].code==20886;conflict=e.args[0].code
 else:raise AssertionError("Changed request accepted")
 c.rollback()
 q.execute("select count(*) from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=:op and PICK_PLAN_ID=:pid",op=op,pid=pid);assert q.fetchone()[0]==1
 q.execute("select count(*) from RRL_PICK_PLAN where CUSTOMER_ORDER_ID=2135 and STATUS!='CANCELLED'");assert q.fetchone()[0]==1
 q.execute("select STATUS,TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY,TOTAL_SHORTAGE_QTY from RRL_PICK_PLAN where PICK_PLAN_ID=:pid",pid=pid);plan=q.fetchone()
 q.execute("select count(*) from RRL_PICK_TASK where PICK_PLAN_ID=:pid",pid=pid);tasks=q.fetchone()[0];assert tasks==0
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT) like '%FROM RRL_PICK_PLAN_CREATE_OP WHERE OPERATION_ID%' and SQL_TEXT not like '%V$SQL%' order by ELAPSED_TIME/nullif(EXECUTIONS,0) desc fetch first 3 rows only")
 top=q.fetchall()
 result={"status":"PASS","plan_id":pid,"replay_ms":elapsed,"content_conflict":conflict,"active_plans":1,"receipt_count":1,"plan":plan,"tasks":tasks,"top_receipt_sql":top}
 print(json.dumps(result))
