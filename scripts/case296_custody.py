exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from concurrent.futures import ThreadPoolExecutor
import httpx,uuid
for number in[291,292]:
 p=Path("tmp/context296_"+str(number)+".json");ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
 saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{}
 if not saved:
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
   req=dict(contract_version=2,operation_id="IW296.ROLL:"+uuid.uuid4().hex,command_type="INTERWARE_CUSTODY_RELEASE",actor="admin",source=dict(receipt_operation_id=ctx["receipt_operation"]),lines=[],units=[],metadata={})
   try:
    q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
    if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
    result=read_oracle_json(out.getvalue());assert result["full_physical_receipt"]is False and result["accepted_quantity"]=="1"and result["confirmed_short_quantity"]=="2",result
    c.rollback();q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op_id",op_id=ctx["source_load"]);assert q.fetchone()==(None,)
   finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  bodies=[dict(operation_id="IW296.CUSTODY:"+uuid.uuid4().hex,receipt_operation_id=ctx["receipt_operation"])for _ in range(2)]
  def send(body):
   with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
    r=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/release-custody",json=body);return body,r.status_code,r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,bodies))
  assert sorted(x[1]for x in results)==[200,409],results
  winner=next(x for x in results if x[1]==200);saved=dict(custody_body=winner[0],custody_result=winner[2])
  p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/release-custody",json=saved["custody_body"]);assert r.status_code==200 and r.json()==saved["custody_result"],r.text
  onward_body=dict(operation_id="IW296.NEXT:"+str(number)+":"+ctx["tag"],receipt_operation_id=ctx["receipt_operation"],reason="Передать следующему плечу только фактически принятое количество",decision_reference="DEV296:accepted1-confirmedloss2")
  r=client.post("http://127.0.0.1:8088/api/inventory/interwarehouse/prepare-onward",json=onward_body);assert r.status_code==200,r.text
  x=r.json();assert x["quantity"]=="1",x;saved["onward_body"]=onward_body;saved["onward_result"]=x;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
print("PASS296 ordinary+marked partial custody rollback/200-409/replay accepted1+confirmedshort2; originalSTconstructor onward1/no repeated fulfillment")
