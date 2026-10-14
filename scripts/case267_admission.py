"""Two existing source264 orders, no new source/demand/stock birth."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.fulfillment.infrastructure.store_orders import StoreOrders
from app.modules.fulfillment.infrastructure.store_admission import StoreAdmission
from app.modules.fulfillment.domain.store_decision import read_store_decision
from app.modules.fulfillment.application.ports import StoreOrderConflict
from app.modules.platform.public import read_oracle_json
from app.workers.sap_artmas_worker import process_batch
from concurrent.futures import ThreadPoolExecutor
import httpx,xml.etree.ElementTree as ET
data=json.loads(Path("tmp/context264.json").read_text(encoding="utf-8"));svc=StoreOrders(OracleGateway());admission=StoreAdmission(OracleGateway())
held=data["held"]["customer_order_id"];accepted=data["accepted"]["customer_order_id"];tag=data["tag"]
source=svc.get(held,"admin");assert source["admission_status"]=="PENDING_CALENDAR"and source["admission_decision"]["version"]==0
def xml(order,decision,suffix,version=0,content_hash=None):
 current=svc.get(order,"admin");r=ET.Element("WarehouseCustomerOrderDecision",version="1")
 fields={"Sender":current["sender"],"MessageId":"DEC267.MSG:"+tag+suffix,"DecisionId":"DEC267.ID:"+tag+suffix,
 "OrderNumber":current["order_number"],"OriginalContentHash":content_hash or current["content_hash"],"ExpectedVersion":str(version),
 "Decision":decision,"Reason":"Own267 explicit simulated ERP source admission decision","Reference":"Own267 source264 current calendar proof, no real SAP acknowledgment"}
 for k,v in fields.items():ET.SubElement(r,k).text=v
 return ET.tostring(r,encoding="utf-8")
body=xml(held,"ACCEPT",".ROLL")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB);payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(read_store_decision(body),sort_keys=True,separators=(",",":")))
 q.callproc("RRL_SAP_STORE_ADMISSION_API.apply_decision",["admin",payload,out]);assert read_oracle_json(out.getvalue())["admission_status"]=="ACCEPTED"
 c.rollback();q.execute("select ADMISSION_STATUS from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:id",id=held);assert q.fetchone()==("PENDING_CALENDAR",)
 q.execute("select count(*)from RRL_SAP_STORE_DECISION where CUSTOMER_ORDER_ID=:id",id=held);assert q.fetchone()==(0,)
try:admission.receive(xml(held,"ACCEPT",".STALE",content_hash="0"*64),"admin")
except StoreOrderConflict:pass
else:raise AssertionError("Content source version bypass")
def send(suffix):
 raw=xml(held,"ACCEPT",suffix)
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post("http://127.0.0.1:8088/api/integrations/sap/store-decisions",content=raw,headers={"Content-Type":"application/xml"})
 return r.status_code,r.json(),raw
with ThreadPoolExecutor(2)as pool:responses=list(pool.map(send,[".A",".B"]))
assert sorted(r[0]for r in responses)==[202,409],[(r[0],r[1])for r in responses]
winner=next(r for r in responses if r[0]==202);decision=winner[1];raw=winner[2]
assert admission.receive(raw,"SAP_FILE_GATEWAY")==decision
root=Path("tmp/gateway267")/tag;(root/"inbox").mkdir(parents=True,exist_ok=True);(root/"inbox"/"same-decision.xml").write_bytes(raw)
results=process_batch(root,20,0,"store-decision");assert results[0]["customer_order_id"]==held and results[0]["version"]==1
assert len(list((root/"archive").glob("*.xml")))==1
changed=ET.fromstring(raw);next(n for n in changed if n.tag=="Decision").text="REJECT"
try:admission.receive(ET.tostring(changed,encoding="utf-8"),"admin")
except StoreOrderConflict:pass
else:raise AssertionError("Message payload conflict")
rejected=admission.receive(xml(accepted,"REJECT",".REJECT"),"SAP_FILE_GATEWAY");assert rejected["admission_status"]=="REJECTED"and rejected["customer_order_status"]=="CANCELLED"
assert svc.get(held,"admin")["admission_status"]=="ACCEPTED"
assert svc.get(held,"admin")["result_json"]["admission_status"]=="PENDING_CALENDAR"
assert svc.receive(data["raw_closed"].encode(),"SAP_FILE_GATEWAY")["admission_status"]=="PENDING_CALENDAR"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select CUSTOMER_ORDER_ID,sum(ORDER_QTY)from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID in(:held,:accepted)group by CUSTOMER_ORDER_ID",held=held,accepted=accepted);assert sorted(q.fetchall())==sorted([(held,1),(accepted,1)])
 q.execute("select count(*)from RRL_SAP_STORE_ORDER");assert q.fetchone()==(2,)
 try:q.execute("update RRL_SAP_STORE_ORDER set ADMISSION_STATUS='ACCEPTED'where CUSTOMER_ORDER_ID=:id",id=accepted)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("Direct admission bypass")
 c.rollback()
 try:q.execute("delete from RRL_SAP_STORE_DECISION where CUSTOMER_ORDER_ID=:id",id=held)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("Decision history deletion")
 c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%FROM RRL_SAP_STORE_DECISION WHERE%'and executions>0 order by last_active_time desc fetch first 4 rows only");print("SQL_MS",q.fetchall())
Path("tmp/context267.json").write_text(json.dumps({"held":held,"accepted":accepted,"decision":decision,"raw":raw.decode(),"rejected":rejected},ensure_ascii=True),encoding="utf-8")
print("PASS267 same2642sourceorders/nativeAtomicrollback/expectedHash/native currentopenCalendar/futuredeadline/concurrentHTTP202-409/sameMsgservice+fileworkerreplay/id-bodyconflict/rejectotherbeforeplans/qty1each-originaltimes-result preserved/directguards/P20H20/no Stock or source birth/ERP XMLsimulatednotrealACK")
