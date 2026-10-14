exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.case_type_composition import build_case_type_service
from app.modules.inventory.public import StockPostingError
ctx=Path("tmp/context1214.json");context=json.loads(ctx.read_text(encoding="utf-8"));assert context["state"]=="EMPTY"
task=context["task"];tag=context["tag"];source={"warehouse_id":context["warehouse"]};service=build_case_type_service()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor()
 current=service.read(task,"admin");assert current["can_change_empty_type"] and current["actual_pallet_type_id"]==1,current
 metadata={"pallet_type_id":3,"expected_version":0,"scan_container":"CASE:"+str(task),"reason":"DEV1214 empty assembly override, software evidence"}
 op="CASE.TYPE1214:"+tag
 command={"contract_version":2,"operation_id":op+".ROLLBACK","command_type":"CASE_PALLET_TYPE_CHANGE","actor":"admin","source":{"case_task_id":task},"lines":[],"units":[],"metadata":metadata}
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None]);q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out]);c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 assert service.read(task,"admin")["actual_pallet_type_id"]==1
 receipt=service.change(task,op,metadata,"admin");assert service.change(task,op,metadata,"admin")==receipt
 after=service.read(task,"admin");assert after["actual_pallet_type_id"]==3 and after["version"]==1
 try:service.change(task,op,{**metadata,"pallet_type_id":2},"admin");raise AssertionError("Same operation changed content accepted")
 except StockPostingError:pass
 try:service.change(task,"CASE.STALE1214:"+tag,{**metadata,"pallet_type_id":2},"admin");raise AssertionError("Stale version accepted")
 except StockPostingError:pass
 try:
  q.execute("update RRL_CASE_PICK_TASK set PALLET_TYPE_ID=2 where CASE_PICK_TASK_ID=:task",task=task);raise AssertionError("Direct type writer admitted")
 except oracledb.DatabaseError as exc:assert "CASE_TYPE_ROOT_OWNER_REQUIRED"in str(exc),str(exc)
 finally:c.rollback()
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
 context.update(state="TYPED_EMPTY",operation=op,receipt=receipt,current=after,protected=[20,20]);ctx.write_text(json.dumps(context,indent=2),encoding="utf-8")
 print(json.dumps({"status":"PASS1214","task":task,"warehouse":source["warehouse_id"],"actual_type":3,"version":1,"quantity_events":0,"protected":[20,20]}))
