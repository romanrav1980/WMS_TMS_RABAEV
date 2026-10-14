exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest
from app.oracle_gateway import OracleGateway
record=json.loads(Path("tmp/context1057.json").read_text(encoding="utf-8"));assert record["stage"]=="DONE"
service=StDeferWaiting(OracleGateway())
req=WaitingTaskRequest(operation_id="HU1057.PLAN:4bb85f1f15",decision_operation_id=record["decision"])
assert service.plan(req,"admin")==record["plan"]
record["plan_replay"]=True
read=service.read(record["decision"],"admin",record["task"]-1,10);task=[t for t in read["tasks"]if t["task_id"]==record["task"]][0]
assert task["status"]=="DONE"and task["quantity"]=="1" and task["base_uom"]=="HU"and task["sync_status"]=="SYNCED"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select p.REMAIN,p.HARD_RESERVED_BASE from RRL_REMAINS p join RRL_CELLS cl on cl.CELL=p.CELL where cl.WARE_ID=6667491")
 protected=q.fetchall();assert sum(x[0]for x in protected)==20 and sum(x[1]for x in protected)==20
 q.execute("select STATUS,count(*)from RRL_TARE_BOOK where OPERATION_ID in('TARE987.BOOK:4bb85f1f15:1131','TARE987.BOOK:4bb85f1f15:1132')group by STATUS");assert q.fetchall()==[("HELD",2)]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,260)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and
 (SQL_TEXT like '%S.ST_NUMBER=:B1 ORDER BY S.ID%'or SQL_TEXT like '%RRL_ST_DEFER_WAIT_RUN%'or SQL_TEXT like '%DEFER_HU%')
 order by LAST_ACTIVE_TIME desc fetch first 8 rows only""")
 sql=[list(x)for x in q.fetchall()]
record["current_waiting_read"]=read;record["protected20"]=True;record["tare_bookings_held"]=True
Path("tmp/context1057.json").write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
Path("tmp/read1064_nested_wait.json").write_text(json.dumps({"task":task,"versions":record["current_versions"],"root":record["current_tree"]["nodes"][0]["version"],"physical_hard":record["physical_hard"],"sql":sql,"native_errors":[],"native_invalid":[],"plan_exact_replay":True},indent=2,default=str),encoding="utf-8")
print("PASS1064 original1149 DONE1HU/SYNCED/twoCASE20/P20H20/planfinalRootoutbox exact replay/tareHELD/protected20/nativeVALID")
print(json.dumps(record["current_versions"]));print("root",record["current_tree"]["nodes"][0]["version"])
