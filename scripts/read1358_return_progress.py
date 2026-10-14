exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",secret),timeout=20)as client:
 result={}
 for source in ["STORE642.RECEIPT:dc1889623c","STORE383.RECEIPT:c09bc5c0","STORE.RECEIPT:da46b595-e71c-477b-b0ae-1f3292fdc0c1"]:
  r=client.get("/api/delivery/store-returns/"+source);print(source,r.status_code)
  if r.status_code!=200:print(r.text[:1500]);continue
  result[source]=r.json();print(json.dumps(r.json()["approvals"],default=str))
 Path("tmp/read1358.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
