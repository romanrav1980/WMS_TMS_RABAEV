exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
import uuid,httpx
from concurrent.futures import ThreadPoolExecutor
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select d.OPERATION_ID,d.REVISION_NO,r.OPERATION_ID,d.PLAN_OPERATION_ID
 from RRL_INTERWARE_DECISION d join RRL_INTERWARE_RECEIPT r on r.PLAN_OPERATION_ID=d.PLAN_OPERATION_ID
 where d.INCIDENT_KIND is not null and r.ORIGINAL_ROOT_UID is null and r.CREATED_AT>d.CREATED_AT
 and d.PLAN_OPERATION_ID like '%1872b69bf4%' order by d.REVISION_NO desc fetch first 1 rows only""")
 row=q.fetchone();assert row,"existing243 full followup required"
 body=dict(incident_operation_id=row[0],incident_revision=int(row[1]),followup_receipt_operation_id=row[2],reason="Фактическая полная приёмка подтверждена складским журналом",evidence_reference="DEV293:actual243-full-receipt")
 def native(op,b,actor="admin"):
  payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(b,sort_keys=True,separators=(",",":"),ensure_ascii=False));out=q.var(oracledb.DB_TYPE_CLOB)
  q.callproc("RRL_INTERWARE_INCIDENT_API.close_case",[op,actor,payload,out]);return read_oracle_json(out.getvalue())
 op="IW293.ROLLBACK:"+uuid.uuid4().hex
 result=native(op,body);assert result["status"]=="CLOSED_AFTER_FULL_RECEIPT"and not result["stock_changed"]
 c.rollback();q.execute("select count(*)from RRL_INTERWARE_INCIDENT_CLOSE where OPERATION_ID=:op_id",op_id=op);assert q.fetchone()==(0,)
 for b,actor,expected in [(dict(body,incident_revision=999999),"admin",20886),(body,"SAP_FILE_GATEWAY",20882),(dict(body,followup_receipt_operation_id=json.loads(Path("tmp/context292.json").read_text())["receipt_operation"]),"admin",20886)]:
  try:native("IW293.NEG:"+uuid.uuid4().hex,b,actor)
  except oracledb.DatabaseError as e:assert e.args[0].code==expected,e
  else:raise AssertionError("invalid closure accepted")
  c.rollback()
 q.execute("select count(*)from RRL_INTERWARE_INCIDENT_CLOSE where INCIDENT_OPERATION_ID=:inc_id",inc_id=row[0]);existing=q.fetchone()[0]
 q.execute("select OPERATION_ID,RESULT_JSON from RRL_INTERWARE_INCIDENT_CLOSE where INCIDENT_OPERATION_ID=:inc_id",inc_id=row[0]);saved=q.fetchone()if existing else None
base="http://127.0.0.1:8088/api/inventory/interwarehouse"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 if not existing:
  bodies=[dict(body,operation_id="IW293.CLOSE:"+uuid.uuid4().hex)for _ in range(2)]
  def send(b):
   with httpx.Client(auth=("admin","admin123"),timeout=30)as session:
    r=session.post(base+"/incident-closures",json=b);return b,r.status_code,r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(send,bodies))
  assert sorted(x[1]for x in results)==[200,409],results
  winner=next(x for x in results if x[1]==200);op=winner[0]["operation_id"];expected=winner[2]
 else:op=saved[0];expected=read_oracle_json(saved[1])
 r=client.post(base+"/incident-closures",json=dict(body,operation_id=op));assert r.status_code==200 and r.json()==expected,r.text
 r=client.post(base+"/incident-closures",json=dict(body,operation_id=op,reason="Другое содержимое подтверждённого решения"));assert r.status_code==409,r.text
 r=client.get(base+"/plans/"+row[3]+"/decisions");assert r.status_code==200,r.text
 assert next(d for d in r.json()["decisions"]if d["operation_id"]==row[0])["incident_close_operation_id"]==op
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 Path("tmp/context293.json").write_text(json.dumps(dict(operation_id=op,body=body,result=expected,plan_operation_id=row[3]),ensure_ascii=False,indent=2),encoding="utf-8")
print("PASS293 actual243 full followup closure/outerrollback/200-409/replay/collision/history/partial-receipt rejection/gateway403/protected20-20")
