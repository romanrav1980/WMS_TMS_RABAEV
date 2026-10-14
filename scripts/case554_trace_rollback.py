exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
import httpx
ctx=json.loads(Path("tmp/context553.json").read_text(encoding="utf-8"));assert ctx["done"]
tag=ctx["tag"];ware=ctx["warehouse"];type_id=ctx["type"];prefix="TRACE554:"+tag
with httpx.Client(auth=("admin","admin123"),timeout=35)as api,oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("select QUANTITY,BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=:type_id and CUSTODIAN_KIND='WAREHOUSE'and CONDITION_CODE='GOOD'",ware=ware,type_id=type_id);qty,version=q.fetchone();assert qty==0
 count={"operation_id":prefix+":COUNT","owner_ware_id":ware,"pallet_type_id":type_id,"condition":"GOOD","observed_quantity":"1","expected_version":version,"reason":"Own554 one asset for rollback","decision_reference":"DEV554:"+tag}
 r=api.post("http://127.0.0.1:8088/api/inventory/tare/count",json=count);assert r.status_code==200,r.text
 try:
  q.execute("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:op",op="TRACE553.DAMAGE:"+tag)
  body=read_oracle_json(q.fetchone()[0]);body["operation_id"]=prefix+":DAMAGE";body["actor"]="admin"
  body["source"]={};body["metadata"]={"owner_ware_id":ware,"pallet_type_id":type_id,"custodian_kind":"WAREHOUSE","custodian_id":str(ware),"quantity":"1","reason":"Own554 rollback damage","decision_reference":"DEV554.DAMAGE:"+tag}
  payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body))
  result=q.var(oracledb.DB_TYPE_CLOB)
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[payload,"admin",result,None]);assert result.getvalue()is None
  q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result]);assert read_oracle_json(result.getvalue())["resolution_kind"]=="DAMAGE"
  q.execute("select QUANTITY from RRL_TARE_DAMAGE_ORIGIN where DAMAGE_OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  q.execute("select QUANTITY from RRL_TARE_DAMAGE_POSITION where DAMAGE_OPERATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1,)
  c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  for table,column in [("RRL_STOCK_OPERATION","OPERATION_ID"),("RRL_TARE_RESOLUTION","OPERATION_ID"),("RRL_TARE_DAMAGE_ORIGIN","DAMAGE_OPERATION_ID"),("RRL_TARE_DAMAGE_POSITION","DAMAGE_OPERATION_ID"),("RRL_EVENT_OUTBOX","CORRELATION_ID")]:
   q.execute(f"select count(*)from {table} where {column}=:op",op=body["operation_id"]);assert q.fetchone()==(0,),table
  q.execute("select CONDITION_CODE,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=:type_id and CUSTODIAN_KIND='WAREHOUSE'order by CONDITION_CODE",ware=ware,type_id=type_id)
  assert q.fetchall()==[("DAMAGED",0),("GOOD",1)]
  print("PASS554 late outer rollback removes origin/position/resolution/stock operation/outbox together; original GOOD1 restored. No commit in trace owner.")
 finally:
  c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=:type_id and CUSTODIAN_KIND='WAREHOUSE'and CONDITION_CODE='GOOD'",ware=ware,type_id=type_id);version=q.fetchone()[0]
  cleanup={**count,"operation_id":prefix+":CLEAN","observed_quantity":"0","expected_version":version,"reason":"Own554 fixture cleanup after rollback"}
  r=api.post("http://127.0.0.1:8088/api/inventory/tare/count",json=cleanup);assert r.status_code==200,r.text
