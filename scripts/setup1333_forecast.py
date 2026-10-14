exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
out=[]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",password),timeout=30)as client:
 for suffix,rate in [("A","12"),("B","6")]:
  body={"operation_id":"NORM1333:B01"+suffix,"warehouse_id":9807,"site_code":"OWN_B01_FULLPAL","article":"QAUTOc0c2a00c0b"+suffix,"base_uom":"EA","base_per_hour":rate,"expected_version":0,"active":True,"reason":"Own B01 dev forecast normative example; not production productivity"}
  r=client.post("/api/resources/workload/norms",json=body);out.append({"kind":"norm","status":r.status_code,"body":r.json()});r.raise_for_status()
 for load in ["TT.LOAD:d00a9887-fee3-4c58-938b-5b18cadebfcb","TT.LOAD:5e037ff9-46be-4c11-8e88-f9d76ed3f3c6"]:
  r=client.post("/api/transport/warehouse-forecast/source",json={"source_load_operation_id":load});out.append({"kind":"projection","status":r.status_code,"body":r.json()});r.raise_for_status()
Path("tmp/setup1333.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(json.dumps(out))
