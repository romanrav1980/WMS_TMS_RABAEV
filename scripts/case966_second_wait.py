exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.modules.platform.public import read_oracle_json
from app.schemas import WarehouseTaskStatusRequest
from decimal import Decimal
from fastapi import HTTPException
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"));path=Path("tmp/context966.json")
assert not path.exists(),"966 registered; continue retained context, no new planning source"
tag=ctx["tag"];ct,cl,carrier,qty,cell=ctx["cases"][1];st=ctx["shipments"][str(ct)];target=ctx["target_trip"];wait=ctx["wait"]
record={"tag":tag,"case":int(ct),"st":st,"carrier":carrier,"quantity":"8","stage":"PREPARED"}
def save():path.write_text(json.dumps(record,indent=2),encoding="utf-8")
save();g=OracleGateway()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:trip where PALLET_UID=:p_uid",trip=ctx["source_trip"],p_uid=st);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 seen=StDeferral(g).context(st,"admin");assert seen["physical_preparation"]["state"]=="PREPARED_CASE"
 body={"st_number":st,"target_trip_id":target,"expected_version":seen["version"],"source_hash":seen["source_hash"],"reason":"Second retained CASE goes to waiting","reference":"WAIT966:"+tag}
 op="DEC966:"+tag;decision=StDeferral(g).defer(op,body,"admin");assert StDeferral(g).defer(op,body,"admin")==decision
 record.update(decision=op,decision_body=body,decision_result=decision,stage="DEFERRED");save()
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["PLAN966:"+tag,op,"admin",out]);plan=read_oracle_json(out.getvalue());c.commit()
 task=int(plan["tasks"][0]["task_id"]);record.update(task=task,plan=plan,stage="PLANNED");save()
 q.execute("select CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));origin,version=q.fetchone()
 req=WarehouseTaskStatusRequest(operation_id="MOVE966:"+tag,updated_by="admin",fact_qty=Decimal("1"),scanned_pallet=carrier,scanned_from_cell=origin,scanned_to_cell=wait)
 record["move_request"]=req.model_dump(mode="json");save()
 partial=req.model_copy(update={"operation_id":"BAD966:"+tag,"unit_keys":["IGNORED.UNIT"]})
 try:complete_existing_task(g,task,partial,"admin");raise AssertionError("Partial unit selection ignored")
 except HTTPException as exc:assert exc.status_code==409 and "NO_PARTIAL_UNIT_SELECTION"in str(exc.detail),str(exc)
 result=complete_existing_task(g,task,req,"admin");assert complete_existing_task(g,task,req,"admin")==result
 record.update(result=result,stage="DONE");save()
 q.execute("select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",1)
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==("SYNCED",)
 q.execute("select UID_PALLET,TARGET_UID_PALLET,BASE_QTY,BASE_UOM,OPERATION_ID from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=task);journal=q.fetchall();assert len(journal)==1 and journal[0][2:]==(8,"EA",req.operation_id),journal
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.REMAIN>0",id=int(ct));assert q.fetchone()==(8,8,wait,wait)
 q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(:op,'AL32UTF8'),sys.dbms_crypto.hash_sh256))",op=req.operation_id);assert q.fetchone()==(1,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 record["journal"]=[list(x)for x in journal];record["evidence"]={"places":"1","goods":"8","hard":"8","current_cell":wait,"sync":"SYNCED","exact_replay":True,"outbox_count":1,"partial_selection_refused":True,"protected_ware_unchanged":True};save()
 print("PASS966 retained secondCASE8/H8 -> existing defer/plan/bridge DONE1/SYNCED/currentlot journal8EA/outbox1/replay/partialunitrefused/protectedwareunchanged")
