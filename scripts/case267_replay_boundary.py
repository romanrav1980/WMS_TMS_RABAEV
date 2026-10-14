exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.fulfillment.domain.store_decision import read_store_decision
from app.modules.platform.public import read_oracle_json
import httpx
data=json.loads(Path("tmp/context267.json").read_text(encoding="utf-8"))
original=read_store_decision(data["raw"].encode())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for field,new_value in [("reason","Forged native reason, same declared payload hash"),("reference","Forged native reference, same declared payload hash"),("raw_xml",data["raw"]+" ")]:
  body=dict(original);body[field]=new_value
  v=q.var(oracledb.DB_TYPE_CLOB);v.setvalue(0,json.dumps(body));result=q.var(oracledb.DB_TYPE_CLOB)
  try:q.callproc("RRL_SAP_STORE_ADMISSION_API.apply_decision",["admin",v,result])
  except oracledb.DatabaseError as e:assert "MESSAGE_PAYLOAD_CONFLICT" in str(e),str(e)
  else:raise AssertionError(field)
  c.rollback()
 body=dict(original);body["unexpected"]="value"
 v=q.var(oracledb.DB_TYPE_CLOB);v.setvalue(0,json.dumps(body));result=q.var(oracledb.DB_TYPE_CLOB)
 try:q.callproc("RRL_SAP_STORE_ADMISSION_API.apply_decision",["admin",v,result])
 except oracledb.DatabaseError as e:assert "INPUT_FIELDS_INVALID" in str(e)
 else:raise AssertionError("Unknown native fields")
 c.rollback()
 q.execute("select count(*)from RRL_SAP_STORE_DECISION");assert q.fetchone()==(2,)
with httpx.Client(auth=("admin","admin123"),timeout=30) as client:
 r=client.post("http://127.0.0.1:8088/api/integrations/sap/store-decisions",content=data["raw"].encode(),headers={"Content-Type":"application/xml"})
 assert r.status_code==202,r.text
 assert r.json()==data["decision"]
print("PASS267 cached native actual material comparison/forged declared hash denied/unknown fields denied/same exact HTTP replay/no new decisions")
