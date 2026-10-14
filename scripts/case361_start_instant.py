exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transaction_gateway import TransactionGateway
from app.modules.resources.infrastructure.case_actions import CaseActions
from app.modules.inventory.infrastructure.case_events import write_case_event
from app.schemas import CasePickTaskActionRequest
from uuid import uuid4
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_SHIFT'and COLUMN_NAME in('START_AT','FINISH_AT')");print(json.dumps(q.fetchall()))
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","case_pick_manage"])
 try:
  tag="CS361:"+uuid4().hex[:10]
  task=q.var(oracledb.DB_TYPE_NUMBER)
  type_out=q.var(oracledb.DB_TYPE_NUMBER)
  q.execute("""declare sample RRL_CASE_PICK_TASK%rowtype;wave_sample RRL_PICK_WAVE%rowtype;wave_id number;task_id number;tare RRL_PALLET_TYPE%rowtype;type_id number;begin
   select *into tare from RRL_PALLET_TYPE where PALLET_TYPE_ID=21;select RRL_PALLET_TYPE_SQ.nextval into type_id from dual;tare.PALLET_TYPE_ID:=type_id;tare.FINAL_WEIGHT_REQUIRED:=0;tare.PALLET_TYPE_CODE:=:tag;tare.PALLET_TYPE_NAME:=:tag;insert into RRL_PALLET_TYPE values tare;:type_out:=type_id;
   select *into sample from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1112;
   select *into wave_sample from RRL_PICK_WAVE where PICK_WAVE_ID=sample.PICK_WAVE_ID;
   select RRL_PICK_WAVE_SQ.nextval into wave_id from dual;wave_sample.PICK_WAVE_ID:=wave_id;wave_sample.WAVE_CODE:=:tag;wave_sample.STATUS:='LAUNCHED';wave_sample.CREATED_BY:='admin';insert into RRL_PICK_WAVE values wave_sample;
   select RRL_CASE_PICK_TASK_SQ.nextval into task_id from dual;sample.CASE_PICK_TASK_ID:=task_id;sample.PALLET_TYPE_ID:=type_id;sample.PICK_WAVE_ID:=wave_id;sample.LEGACY_SBORKA_PALLET_ID:=null;sample.STATUS:='NEW';sample.SSCC:=:tag;sample.ASSIGNED_TO:=null;sample.ASSIGNED_RESOURCE_ID:=null;sample.RESOURCE_SESSION_ID:=null;sample.EQUIPMENT_ID:=null;sample.STARTED_AT:=null;sample.STARTED_AT_INSTANT:=null;sample.STARTED_SHIFT_TIME_ZONE:=null;sample.CLOSED_AT:=null;sample.DONE_AT:=null;sample.TRANSFERRED_AT:=null;sample.TOTAL_LINES:=0;sample.PICKED_LINES:=0;sample.PLANNED_QTY:=0;sample.PICKED_QTY:=0;
   insert into RRL_CASE_PICK_TASK values sample;:task_out:=task_id;
  end;""",tag=tag,task_out=task,type_out=type_out)
  tid=int(task.getvalue());tare_type=int(type_out.getvalue());c.commit();q.callproc("RRL_STOCK_METADATA_TX.end_change")
  client=httpx.Client(auth=("admin","admin123"),timeout=40)
  def post(path,body):
   r=client.post("http://127.0.0.1:8088/api"+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1500]);return r.json()
  q.execute("select WARE_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=tid);ware,carrier,version=q.fetchone()
  Path("tmp/context361.json").write_text(json.dumps({"task":tid,"type":tare_type,"ware":ware,"tag":tag,"carrier":carrier,"version":int(version)}),encoding="utf-8")
  post("/inventory/tare/count",{"operation_id":tag+":COUNT","owner_ware_id":int(ware),"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own empty CASE clock fixture","decision_reference":tag})
  post("/inventory/tare/book",{"operation_id":tag+":BOOK","place_kind":"CASE","place_id":str(tid)})
  q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","case_pick_manage"])
  bound=TransactionGateway(q);actions=CaseActions(bound,write_case_event);request=CasePickTaskActionRequest(actor="admin")
  actions.start_task(tid,request)
  q.execute("select STARTED_AT_INSTANT,STARTED_SHIFT_TIME_ZONE from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=tid);instant,zone=q.fetchone();assert instant is not None and instant.tzinfo is not None and zone is None
  actions.start_task(tid,request)
  q.execute("select count(*)from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='STARTED'",id=tid);assert q.fetchone()[0]==1
  try:q.execute("update RRL_CASE_PICK_TASK set STARTED_AT_INSTANT=STARTED_AT_INSTANT-interval '1'hour where CASE_PICK_TASK_ID=:id",id=tid)
  except oracledb.DatabaseError as e:assert e.args[0].code==20863,str(e)
  else:raise AssertionError("Actual start clock changed")
  c.rollback()
  q.execute("select STARTED_AT_INSTANT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=tid);assert q.fetchone()[0]is None
  q.callproc("RRL_STOCK_METADATA_TX.end_change")
  post(f"/case-pick/tasks/{tid}/return-carrier",{"operation_id":tag+":RETURN","scan_container":carrier,"expected_content_version":int(version),"destinations":{},"allow_empty":True,"reason":"Finish owned empty clock fixture after rollback"})
  post("/inventory/tare/book-cancel",{"operation_id":tag+":CANCEL","booking_operation_id":tag+":BOOK"})
  q.execute("select BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=:w and PALLET_TYPE_ID=:t and CONDITION_CODE='GOOD'and CUSTODIAN_KIND='WAREHOUSE'",w=ware,t=tare_type)
  bv=int(q.fetchone()[0])
  post("/inventory/tare/count",{"operation_id":tag+":ZERO","owner_ware_id":int(ware),"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":"0","expected_version":bv,"reason":"Retire own empty CASE clock fixture","decision_reference":tag})
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 finally:
  c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
print("PASS361 original CASE START/currentserver awareinstant/unknownshiftzone explicit/one event onrepeat/immutableclock/whole metadata rollback/no goods")
