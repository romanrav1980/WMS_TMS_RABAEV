exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
p=Path("tmp/context1238.json");ctx=json.loads(p.read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'");actor,password=q.fetchone()
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 r=client.patch("/api/admin/transport/tasks/33571",json={"voditel_id":ctx["loading_driver"]["id"],"dock":ctx["loading_dock"]})
 print(json.dumps({"trip":r.status_code,"body":r.json()}));r.raise_for_status()
 ctx["loading_trip_configured"]=r.json();p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 r=client.get("/api/admin/transport/vehicles/10059/profile");r.raise_for_status();profile=r.json()
 if profile["state"]=="NOT_CONFIGURED":
  body={"operation_id":"B01.PROFILE1282:c0c2a00c0b","vehicle_id":10059,"expected_source_hash":profile["base_hash"],"expected_version":profile["version"],"vehicle_size_class":"DEV_2_EU","cargo_length_mm":2400,"cargo_width_mm":1600,"cargo_height_mm":2400,"floor_variants":[{"code":"TWO_EU","limits":[{"pallet_type_id":1,"max_places":2}]}],"reason":"Own retained B01 dev fixture; not measured production vehicle","evidence_reference":"OWN.DEV.B01.1282"}
  ctx["loading_profile_request"]=body;p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
  r=client.post("/api/admin/transport/vehicle-profiles",json=body);print(json.dumps({"profile":r.status_code,"body":r.json()}));r.raise_for_status()
  ctx["loading_profile_result"]=r.json();p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
