exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
p=Path("tmp/context1238.json");ctx=json.loads(p.read_text(encoding="utf-8"))
assert ctx["stage"]=="FULLPAL_BOUND"
dock="B01"+ctx["tag"][:8]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'");actor,password=q.fetchone()
 q.execute("select WARE_ID from RRL_TT_DOCK where DOCK=:d",d=dock);row=q.fetchone()
 if row:assert row[0]==9807
 else:q.execute("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:d,9807,0)",d=dock);c.commit()
ctx["loading_dock"]=dock;p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 for url in ["/api/admin/transport/vehicles/10059/profile","/api/admin/transport/vehicle-profiles/tare-types"]:
  r=client.get(url);r.raise_for_status();print(json.dumps({"url":url,"body":r.json()}))
 if not ctx.get("loading_driver"):
  r=client.post("/api/admin/transport/drivers",json={"name":"DEV B01 c0c2a00c","company":"OWN.QA"});r.raise_for_status()
  ctx["loading_driver"]=r.json();p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 print(json.dumps({"driver":ctx["loading_driver"],"dock":dock}))
