exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
ctx_path=Path("tmp/context565.json");ctx=json.loads(ctx_path.read_text(encoding="utf-8"));assert not ctx.get("done"),"Proof already recorded"
trip=ctx["trip"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SOURCE_JSON,SOURCE_STATE,PROFILE_VERSION from RRL_TT_VEHICLE_SOURCE where TT_ID=:trip",trip=trip)
 wire,state,version=q.fetchone();wire=read_oracle_json(wire)
 assert state=="READY"and version==1 and wire["vehicle_profile"]["profile"]["vehicle_size_class"]=="DEV.PROFILE565",wire
 q.execute("select count(*),sum(case when l.DEPARTED_AT=s.CAPTURED_AT then 1 else 0 end)from RRL_TT_HU_LOAD_FACT l join RRL_TT_VEHICLE_SOURCE s on s.TT_ID=l.TT_ID and s.DEPARTURE_OPERATION_ID=l.DEPARTURE_OPERATION_ID where s.TT_ID=:trip",trip=trip);assert q.fetchone()==(1,1)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=wire["departure_operation_id"]);assert q.fetchone()==(0,)
 q.execute("select count(*)from RRL_TT_VEHICLE_SOURCE where TT_ID=33622");assert q.fetchone()==(0,),"Old trip must not get inferred dimensions"
 ctx["source"]=wire;ctx["done"]=True;ctx_path.write_text(json.dumps(ctx),encoding="utf-8")
 print("PASS566 retained new565 actual LOAD/DEPART captured profile1/carrier/type/region/one clock, no second goods effect, old519 source remains unknown. No source recreated.")
