exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,secrets
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"))
actor="OWN1306_DRIVER";group="OWN1306_DRIVER"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select ID,PASS from RUSERS where ID='admin'");admin,adminpass=q.fetchone()
 q.execute("select count(*)from RUSERS where ID=:id",id=actor)
 if q.fetchone()[0]==0:
  q.execute("insert into USER_GROUP(ID,NAME)values(:id,'Owned B03 driver only')",id=group)
  q.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED)values(:id,'Owned B03 driver',:password,:group_id,9807,0)",id=actor,password=secrets.token_urlsafe(18),group_id=group)
  c.commit()
 q.execute("select PASS from RUSERS where ID=:id",id=actor);password=q.fetchone()[0]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=(admin,adminpass),timeout=30)as client:
 r=client.post("/api/admin/rights/groups/OWN1306_DRIVER/rights",json={"right_name":"driver_return_accept","description":"Owned B03 driver binding"});r.raise_for_status()
 r=client.get("/api/transport/driver-bindings/10018");r.raise_for_status();binding=r.json()
 if not binding.get("user_id"):
  r=client.put("/api/transport/driver-bindings/10018",json={"user_id":actor,"active":True,"expected_version":0});r.raise_for_status()
 else:assert binding["user_id"]==actor,binding
 # Own synthetic address had no policy in read1301; create once only.
 if not ctx.get("store_policy1306"):
  r=client.put("/api/delivery/store-receipts/policy",json={"store_address":ctx["store_address"],"mode":"BARCODE","expected_version":0});r.raise_for_status()
  ctx["store_policy1306"]=r.json()
with httpx.Client(base_url="http://127.0.0.1:8088",auth=(actor,password),timeout=30)as client:
 out={}
 for name,url in {"trips":"/api/driver/trips?driver_id=10018&trip_date=2026-11-03","sts":"/api/driver/trips/33571/sts?driver_id=10018","ops":"/api/driver/trips/33571/ops?driver_id=10018","denied":"/api/driver/trips?driver_id=10019&trip_date=2026-11-03"}.items():
  r=client.get(url);out[name]={"status":r.status_code,"body":r.json()}
 ctx["driver_read1306"]=out;ctx["driver_actor"]=actor
Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print(json.dumps(out))
