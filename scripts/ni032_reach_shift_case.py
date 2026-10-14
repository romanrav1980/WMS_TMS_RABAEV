"""One metadata-only case: MAIN offsets, DUTY capacity and mandatory handover before logout."""
import sys,json
from pathlib import Path
from datetime import datetime,timedelta
from uuid import uuid4
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.resources.infrastructure.reach_shifts import ReachShifts
from app.services.resource_management_service import ResourceManagementService
from app.schemas import ResourceShiftCreateRequest,ResourceCreateRequest,ResourceSessionLoginRequest,ResourceSessionStatusRequest
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.contracts_stock import StockCommand
from fastapi import HTTPException
g=OracleGateway();manager=ResourceManagementService(g);svc=ReachShifts(g);tag=uuid4().hex[:10];group="QSG"+tag
def meta(sql,**b):
 with g.transaction("Own reach shift metadata") as c:
  c.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:c.execute(sql,b)
  finally:c.callproc("RRL_STOCK_CONFIG_API.end_change")
def scalar(sql,**b):return next(iter(g.fetch_all(sql,b)[0].values()))
now=datetime.now().replace(microsecond=0)
base=manager.create_shift(ResourceShiftCreateRequest(shift_code="QBASE"+tag,shift_date=now.date(),ware_id=1,
 start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=6),status="OPEN",created_by="admin"))
derived=svc.create(base,2,1,"admin");assert svc.create(base,2,1,"admin")==derived
main,duty=derived["shifts"]
assert main["start_at"]==now-timedelta(minutes=1,hours=2) and main["finish_at"]==now+timedelta(hours=4)
assert duty["finish_at"]==now+timedelta(hours=6)
try:svc.create(base,2,2,"admin");raise AssertionError("Changed counts accepted")
except HTTPException as exc:assert exc.status_code==409
meta("insert into USER_GROUP(ID,NAME) values(:id,'QA shift fixture')",id=group)
resources=[];sessions=[];wave=None
try:
 typ=scalar("select RESOURCE_TYPE from RRL_RESOURCE_TYPE where ACTIVE=1 and instr(DEFAULT_TASK_TYPES,'REPLENISHMENT')>0 and rownum=1")
 for n in range(2):
  user="QSD"+str(n)+tag
  meta("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED) values(:id,'QA shift driver','qa-test-only',:g,0)",id=user,g=group)
  resources.append(manager.create_resource(ResourceCreateRequest(resource_code=user,resource_name=user,resource_type=typ,ware_id=1,user_id=user,created_by="admin")))
 first=manager.login_session(ResourceSessionLoginRequest(shift_id=duty["shift_id"],resource_id=resources[0],operator_user_id="QSD0"+tag,created_by="admin"));sessions.append(first)
 try:
  manager.login_session(ResourceSessionLoginRequest(shift_id=duty["shift_id"],resource_id=resources[1],operator_user_id="QSD1"+tag,created_by="admin"))
  raise AssertionError("Duty driver capacity exceeded")
 except HTTPException as exc:assert exc.status_code==409 and "CAPACITY" in str(exc.detail)
 wave=int(scalar("select RRL_PICK_WAVE_SQ.nextval from dual"))
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS) values(:id,:code,1,'LAUNCHED')",id=wave,code="QSHIFT"+tag)
 task=int(scalar("select RRL_WAREHOUSE_TASK_SQ.nextval from dual"))
 target=scalar("select CELL from RRL_CELLS where WARE_ID=1 and rownum=1")
 meta("""insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,QTY,STATUS,TO_CELL,
 ASSIGNED_TO,RESOURCE_ID,RESOURCE_SESSION_ID) values(:id,'WAVE','REPLENISHMENT','PICK_WAVE',:wave,1,'ASSIGNED',:cell,:owner,:p_resource,:session_id)""",
 id=task,wave=wave,cell=target,owner="QSD0"+tag,p_resource=resources[0],session_id=first)
 try:
  manager.logout_session(first,ResourceSessionStatusRequest(updated_by="admin"));raise AssertionError("Assigned work abandoned")
 except HTTPException as exc:assert exc.status_code==409 and exc.detail["code"]=="SHIFT_HANDOVER_REQUIRED"
 StockPosting().post(StockCommand(operation_id="SHIFT.QA.CANCEL:"+tag,command_type="WAVE_CANCEL",actor="admin",lines=(),
  source={"document_type":"PICK_WAVE","document_id":wave},metadata={"reason":"Close metadata-only fixture","only_cancelled_replenishment":0,"reservation_kind":None}))
 wave=None
 manager.logout_session(first,ResourceSessionStatusRequest(updated_by="admin"));sessions.remove(first)
 print(json.dumps({"passed":True,"base_shift":base,"main":main["shift_id"],"duty":duty["shift_id"],"case":"MAIN minus2h, DUTY till warehouse end, idempotent planning, capacity1 and handover guard"}),flush=True)
finally:
 if wave is not None:
  meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where SOURCE_DOC_ID=:wave and TASK_SOURCE='WAVE'",wave=wave)
  meta("update RRL_PICK_WAVE set STATUS='CANCELLED' where PICK_WAVE_ID=:wave",wave=wave)
 for session in sessions:manager.logout_session(session,ResourceSessionStatusRequest(updated_by="admin"))
 meta("update RRL_RESOURCE_SHIFT set STATUS='CLOSED' where SHIFT_ID=:id or BASE_SHIFT_ID=:id",id=base)
 for resource in resources:meta("update RRL_RESOURCE set ACTIVE=0 where RESOURCE_ID=:id",id=resource)
 meta("update RUSERS set DELETED=1 where USER_GROUP=:g",g=group)
 print("Own schedule/resources closed; no stock created or changed",flush=True)
