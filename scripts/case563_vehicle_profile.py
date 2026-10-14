"""New private vehicle metadata only; no existing fleet rows or goods changed."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from app.services.transport_service import TransportService
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
from app.modules.platform.public import read_oracle_json
ctx_path=Path("tmp/context563.json");assert not ctx_path.exists(),"One-time metadata fixture; use retained exact requests"
tag=uuid4().hex[:8]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select min(TRANSPORTTYPE)from RRL_TRANSPORT_TYPE");vehicle_type=q.fetchone()[0]
vehicle=TransportService().create_vehicle("VP563"+tag,vehicle_type,10000,20,False,"OWN.PROFILE563."+tag)
service=VehicleProfiles(OracleGateway());before=service.read(vehicle,"admin");assert before["state"]=="NOT_CONFIGURED"
body={"operation_id":"VEH.PROFILE563:"+tag,"vehicle_id":vehicle,"vehicle_size_class":"DEV.PROFILE563","cargo_length_mm":6000,"cargo_width_mm":2400,"cargo_height_mm":2600,"expected_version":0,"expected_source_hash":before["base_hash"],"reason":"Own563 declared test dimensions","evidence_reference":"DEV563:"+tag}
ctx={"tag":tag,"vehicle_id":vehicle,"request":body};ctx_path.write_text(json.dumps(ctx),encoding="utf-8")
def publish(request):return VehicleProfiles(OracleGateway()).configure(request,"admin")
with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(publish,[body,body]))
assert results[0]==results[1] and results[0]["version"]==1
ctx["result"]=results[0];ctx_path.write_text(json.dumps(ctx),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_VEHICLE_PROFILE_HIST where VEHICLE_ID=:vehicle",vehicle=vehicle);assert q.fetchone()==(1,)
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","transport_fleet_edit"])
 try:q.execute("update RRL_TR_VEHICLE set PALLETS=21 where ID=:vehicle",vehicle=vehicle);c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
current=service.read(vehicle,"admin");assert current["state"]=="BASE_CHANGED"
assert service.configure(body,"admin")==results[0]
try:service.configure({**body,"operation_id":"VEH.PROFILE563.STALE:"+tag,"expected_version":1},"admin");raise AssertionError("Stale vehicle base accepted")
except Exception as exc:assert "VEHICLE_PROFILE_BASE_CHANGED"in str(exc),str(exc)
new={**body,"operation_id":"VEH.PROFILE563.V2:"+tag,"expected_version":1,"expected_source_hash":current["base_hash"],"reason":"Own563 confirm changed base"}
result=service.configure(new,"admin");assert result["version"]==2 and service.read(vehicle,"admin")["state"]=="READY"
ctx["request_v2"]=new;ctx["result_v2"]=result;ctx_path.write_text(json.dumps(ctx),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();trial={**new,"operation_id":"VEH.PROFILE563.ROLLBACK:"+tag,"expected_version":2}
 result_bind=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_VEHICLE_PROFILE_API.configure",[json.dumps(trial),"admin",result_bind]);assert read_oracle_json(result_bind.getvalue())["version"]==3
 c.rollback();q.execute("select VERSION_NO from RRL_VEHICLE_PROFILE_HEAD where VEHICLE_ID=:vehicle",vehicle=vehicle);assert q.fetchone()==(2,)
 q.execute("select count(*)from RRL_VEHICLE_PROFILE_HIST where OPERATION_ID=:op",op=trial["operation_id"]);assert q.fetchone()==(0,)
 try:q.execute("delete from RRL_VEHICLE_PROFILE_HIST where VEHICLE_ID=:vehicle",vehicle=vehicle);raise AssertionError("History removed")
 except oracledb.DatabaseError as exc:c.rollback();assert "IMMUTABLE"in str(exc)
 q.execute("select count(*)from RRL_TT_VEHICLE_SOURCE where VEHICLE_ID=:vehicle",vehicle=vehicle);assert q.fetchone()==(0,),"No old departure inference"
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_VEHICLE_PROFILE_HIST%'or upper(SQL_TEXT)like '%INTO RRL_VEHICLE_PROFILE_HEAD%')
 order by LAST_ACTIVE_TIME desc fetch first 3 rows only""");print("SQL563",json.dumps(q.fetchall()))
print("PASS563 private existing-fleet vehicle profile same-op concurrent v1 once; changed base invalidates current profile, old replay retained, stale hash refused, v2/current base confirmed; late rollback v3 absent; immutable/no old departure or stock effect.")
