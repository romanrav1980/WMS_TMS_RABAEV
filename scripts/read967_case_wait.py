exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.schemas import WarehouseTaskStatusRequest
from fastapi import HTTPException
ctx=json.loads(Path("tmp/context955.json").read_text(encoding="utf-8"));other=json.loads(Path("tmp/context966.json").read_text(encoding="utf-8"))
evidence={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for record,key in((ctx,"first"),(other,"second")):
  op=record.get("move_operation",record.get("move_request",{}).get("operation_id"));task=record["task"];caseid=record["case"]
  q.execute("select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:k",k="STOCK:"+hashlib.sha256(op.encode()).hexdigest().upper());assert q.fetchone()==(1,)
  q.execute("select STATUS,FACT_QTY,TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);t=q.fetchone();assert t[:2]==("DONE",1)
  q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==("SYNCED",)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.REMAIN>0",id=caseid);stock=q.fetchone();assert stock[:2]==((12,12)if key=="first"else(8,8))
  q.execute("select BASE_QTY,BASE_UOM,OPERATION_ID from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=task);journal=q.fetchall()
  if key=="second":assert journal==[(8,"EA",op)],journal
  evidence[key]={"task":task,"case":caseid,"task_status":t[0],"task_places":str(t[1]),"cell":t[2],"goods":str(stock[0]),"hard":str(stock[1]),"journal":[list(x)for x in journal],"outbox":1}
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like 'SELECT%RRL_CASE_CARRIER_LOT%'and executions>0 order by last_active_time desc fetch first 5 rows only");evidence["sql"]=q.fetchall()
request=WarehouseTaskStatusRequest(**other["move_request"])
again=complete_existing_task(OracleGateway(),other["task"],request,"admin");assert again==other["result"];evidence["second_bridge_replay"]=True
collision=request.model_copy(update={"scanned_to_cell":ctx["src"]})
try:complete_existing_task(OracleGateway(),other["task"],collision,"admin");raise AssertionError("Changed operation content admitted")
except HTTPException as exc:assert exc.status_code==409 and "OPERATION_CONFLICT"in str(exc.detail),str(exc);evidence["changed_same_operation_refused"]=True
# Current source and actor scope are checked before a cached response.
try:complete_existing_task(OracleGateway(),other["task"],request,"QA172_KRO");raise AssertionError("Foreign current actor admitted")
except HTTPException as exc:assert exc.status_code==403 and "WAREHOUSE_FORBIDDEN"in str(exc.detail),str(exc);evidence["foreign_current_actor_refused"]=True
other["evidence"]=evidence["second"];other["checks"]=evidence;Path("tmp/context966.json").write_text(json.dumps(other,indent=2),encoding="utf-8")
Path("tmp/case_wait967.json").write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print(json.dumps(evidence,ensure_ascii=True))
