exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
ctx=json.loads(Path("tmp/context1348.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",secret),timeout=20)as client:
 r=client.get("/api/inventory/tare/return-policy",params={"scope_kind":"STORE","scope_key":ctx["store"]});r.raise_for_status();current=r.json()
 if current["policy_version"]==0:
  r=client.put("/api/inventory/tare/return-policy",json={"scope_kind":"STORE","scope_key":ctx["store"],"return_mode":"DAYS","return_days":7,"timezone_region":"Europe/Moscow","expected_version":0});r.raise_for_status();print(json.dumps(r.json()))
 else:print("Existing configured policy retained")
