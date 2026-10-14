exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.transaction_gateway import TransactionGateway
from app.modules.resources.infrastructure.case_actions import CaseActions
from app.modules.inventory.infrastructure.case_events import write_case_event
from app.schemas import CasePickTaskActionRequest
import httpx
ctx=json.loads(Path("tmp/context361.json").read_text());tid=ctx["task"];tag=ctx["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c,httpx.Client(auth=("admin","admin123"),timeout=40)as client:
 q=c.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","case_pick_manage"])
 try:
  actions=CaseActions(TransactionGateway(q),write_case_event);request=CasePickTaskActionRequest(actor="admin")
  actions.start_task(tid,request)
  q.execute("""select to_char(STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM'),STARTED_SHIFT_TIME_ZONE from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id""",id=tid);instant,zone=q.fetchone();assert instant and len(instant)==25 and zone is None
  actions.start_task(tid,request)
  q.execute("select count(*)from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='STARTED'",id=tid);assert q.fetchone()[0]==1
  try:q.execute("update RRL_CASE_PICK_TASK set STARTED_AT_INSTANT=STARTED_AT_INSTANT-interval '1'hour where CASE_PICK_TASK_ID=:id",id=tid)
  except oracledb.DatabaseError as e:assert e.args[0].code==20863,str(e)
  else:raise AssertionError("Actual start changed")
 finally:c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
 q.execute("select STARTED_AT_INSTANT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=tid);assert q.fetchone()[0]is None
 def post(path,body):
  r=client.post("http://127.0.0.1:8088/api"+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1400]);return r.json()
 post("/inventory/tare/book-cancel",{"operation_id":tag+":CANCEL","booking_operation_id":tag+":BOOK"})
 q.execute("select BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=:w and PALLET_TYPE_ID=:t and CONDITION_CODE='GOOD'and CUSTODIAN_KIND='WAREHOUSE'",w=ctx["ware"],t=ctx["type"]);bv=int(q.fetchone()[0])
 post("/inventory/tare/count",{"operation_id":tag+":ZERO","owner_ware_id":ctx["ware"],"pallet_type_id":ctx["type"],"condition":"GOOD","observed_quantity":"0","expected_version":bv,"reason":"Retire own empty CASE clock fixture","decision_reference":tag})
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","case_pick_manage"]);q.execute("update RRL_CASE_PICK_TASK set STATUS='CANCELLED' where CASE_PICK_TASK_ID=:id and STATUS='NEW' and STARTED_AT is null",id=tid);c.commit();q.callproc("RRL_STOCK_METADATA_TX.end_change")
 ctx.update({"verified_instant":instant,"start_rolled_back":True,"fixture_closed":True});Path("tmp/context361.json").write_text(json.dumps(ctx),encoding="utf-8")
print("PASS361 nativeCASE start/aware Oracle offset/unknown shift zone/one event/repeat/immutable clock/rollback/empty-fixture-retired/tare0/protected20")
