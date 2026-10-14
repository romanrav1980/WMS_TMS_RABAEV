exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));cell="DW753"+ctx["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,2,1,0,0,0,0,0)",cell=cell,ware=ctx["ware"])
  q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
  q.execute("select RRL_WAREHOUSE_TASK_SQ.nextval from dual");task=q.fetchone()[0]
  q.execute("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY)values(:id,'PUTAWAY','MANUAL',:id,'MANUAL',:st,:p_uid,:src,:dst,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,st=ctx["ids"][8],p_uid=ctx["lot"],src=ctx["dst"],dst=cell,ware=ctx["ware"])
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 c.commit();Path("tmp/context753.json").write_text(json.dumps({"task":task,"cell":cell}),encoding="utf-8")
 try:
  request={"contract_version":2,"operation_id":"PROBE753:"+ctx["tag"],"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"3","scanned_pallet":ctx["lot"],"scanned_from_cell":ctx["dst"],"scanned_to_cell":cell}}
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  result=read_oracle_json(out.getvalue());q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=cell);print("TRIAL_TARGET",q.fetchone(),"TASK_RESULT",result.get("status"))
 except oracledb.DatabaseError as e:print("SUPPORTED_REFUSAL",str(e.args[0]).split("\n")[0])
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=ctx["dst"]);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_CELLS where CELL=:cell",cell=cell);assert q.fetchone()==(1,)
from app.services.warehouse_task_service import WarehouseTaskService
from app.oracle_gateway import OracleGateway
from app.schemas import WarehouseTaskStatusRequest
WarehouseTaskService(OracleGateway()).cancel_task(task,WarehouseTaskStatusRequest(updated_by="admin",reason="Bounded manual-task dry-run finished; original picked reserve preserved"))
print("753 quantity trial rolled back; fresh metadata task cancelled through existing action; cell retained for next waiting plan")
