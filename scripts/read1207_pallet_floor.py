import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=json.loads(Path("tmp/context1206.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME in ('RRL_PALLET_FLOOR_READ','RRL_STOCK_PALLET_TYPE_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_LOAD_FLOOR') order by NAME,SEQUENCE")
 errors=q.fetchall();assert not errors,errors
 q.execute("select TYPE_VERSION,PALLET_TYPE_ID,LAST_OPERATION_ID from RRL_PALLET_FLOOR_TYPE where UID_PALLET=:p_uid",p_uid=d["lot"]);typed=q.fetchone();assert typed==(1,1,d["type_operation"])
 q.execute("select PALLET_TYPE_ID,TYPE_ORIGIN,SOURCE_REFERENCE from RRL_TT_LOAD_FLOOR_FACT where LOAD_OPERATION_ID=:op",op=d["load_operation_id"]);proof=q.fetchone();assert proof==(1,"ROOT_STOCK_TYPE",d["type_operation"])
 q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=d["lot"]);stock=q.fetchone();assert stock==(0,0)
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,180)from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%' and (SQL_TEXT like '%RRL_PALLET_FLOOR_TYPE%' or SQL_TEXT like '%PLAN_TARE_BOUND1186%') order by ELAPSED_TIME/nullif(EXECUTIONS,0) desc fetch first 4 rows only")
 slow=q.fetchall()
 result={"status":"PASS_READ_ONLY","trip":d["trip_id"],"native_errors":errors,"type":typed,"loading_proof":proof,"stock":stock,"slow_sql":slow,"decision":"Retain primary UID and bounded ST lookups; no new index. Owner: inventory/transport."}
 Path("tmp/evidence1207.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print(json.dumps(result))
