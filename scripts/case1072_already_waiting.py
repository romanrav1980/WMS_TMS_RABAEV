exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.st_defer_waiting import StDeferWaiting
from app.modules.inventory.contracts_waiting_tasks import WaitingTaskRequest,WaitingTaskError
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
source=json.loads(Path("tmp/context1069.json").read_text(encoding="utf-8"));assert source["stage"]=="DONE"
path=Path("tmp/context1072.json");assert not path.exists() or json.loads(path.read_text(encoding="utf-8"))["stage"]=="NEW","Use saved request replay after execution"
record={"source":1069,"root":source["root"],"decision":source["decision"],"stage":"NEW"}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save();g=OracleGateway();hu=WarehouseHu(g);waiting=StDeferWaiting(g)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 before=hu.preview(source["root"],"admin")
 q.execute("select count(*)from RRL_WAREHOUSE_TASK where UID_PALLET=:p_uid",p_uid=source["root"]);count_before=q.fetchone()[0]
 op="HU1072.ALREADY:4bb85f1f15";req=WaitingTaskRequest(operation_id=op,decision_operation_id=source["decision"])
 result=waiting.plan(req,"admin");assert result["tasks"]==[] and result["already_waiting"]==[source["root"]]and result["stock_changed"]is False
 assert waiting.plan(req,"admin")==result
 q.execute("select count(*)from RRL_WAREHOUSE_TASK where UID_PALLET=:p_uid",p_uid=source["root"]);assert q.fetchone()[0]==count_before
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==0
 assert hu.preview(source["root"],"admin")==before
 try:
  waiting.plan(WaitingTaskRequest(operation_id="HU1069.CREATE:4bb85f1f15",decision_operation_id=source["decision"]),"admin")
  raise AssertionError("Unrelated stock operation ID reused")
 except WaitingTaskError as exc:
  assert exc.status==409 and "DEFER_WAIT_OPERATION_PAYLOAD_CONFLICT" in str(exc)
 q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID='HU1069.CREATE:4bb85f1f15'");assert q.fetchone()[0]==0
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,260)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and
 (SQL_TEXT like '%V_ST_NUMBER%ORDER BY%'or SQL_TEXT like '%RRL_STOCK_OPERATION OP WHERE OP.OPERATION_ID%'or SQL_TEXT like '%DEFER_HU%')
 order by LAST_ACTIVE_TIME desc fetch first 8 rows only""")
 sql=[list(x)for x in q.fetchall()]
 record.update(stage="DONE",request=req.model_dump(),result=result,exact_replay=True,no_new_task=True,no_stock_command=True,versions_unchanged=True,root_id_collision_refused=True,tree=before,sql=sql)
 save()
 print("DONE1072 alreadyWaiting originaldeepTOP/no newtask/no stockcommand/unchangedversions/exactreplay/unrelatedRootID409/nativeVALID")
