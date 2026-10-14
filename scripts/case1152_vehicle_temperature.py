"""One private fleet metadata case; no stock, trip, loading or old profile mutations."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from app.services.transport_service import TransportService
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
from app.modules.transport.domain.temperature_preflight import temperature_preflight
from app.modules.transport.api.vehicle_profile_routes import VehicleProfileRequest
from app.modules.platform.public import read_oracle_json
context=Path("tmp/context1152.json");assert not context.exists(),"Retained one-time metadata fixture; do not recreate"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_VEHICLE_PROFILE_API'");assert q.fetchall()==[]
 q.execute("select OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_VEHICLE_PROFILE_API'");assert all(x[1]=="VALID"for x in q)
 q.execute("select min(TRANSPORTTYPE)from RRL_TRANSPORT_TYPE");vehicle_type=q.fetchone()[0]
tag=uuid4().hex[:8]
vehicle=TransportService().create_vehicle("VT1152"+tag,vehicle_type,10000,20,False,"OWN.TEMP1152."+tag)
service=VehicleProfiles(OracleGateway());before=service.read(vehicle,"admin")
body={"operation_id":"VEH.TEMP1152:"+tag,"vehicle_id":vehicle,"vehicle_size_class":"DEV.TEMP1152",
      "cargo_length_mm":6000,"cargo_width_mm":2400,"cargo_height_mm":2600,
      "expected_version":0,"expected_source_hash":before["base_hash"],
      "reason":"Private1152 capability metadata case, not physical measurement","evidence_reference":"DEV1152:"+tag,
      "temp_min_c":"-20.125","temp_max_c":"6.250"}
context.write_text(json.dumps({"vehicle_id":vehicle,"body":body}),encoding="utf-8")
assert VehicleProfileRequest(**body).model_dump(mode="json",exclude_none=True)==body
for invalid in({"temp_min_c":"7","temp_max_c":"6"},{"temp_min_c":"2","temp_max_c":None},{"temp_min_c":"NaN","temp_max_c":"6"}):
 try:VehicleProfileRequest(**{**body,**invalid})
 except ValueError:pass
 else:raise AssertionError("Invalid API thermal range accepted")
with ThreadPoolExecutor(max_workers=2)as pool:
 results=list(pool.map(lambda _:VehicleProfiles(OracleGateway()).configure(body,"admin"),range(2)))
assert results[0]==results[1] and results[0]["version"]==1
assert results[0]["temperature_capability"]["temp_min_c"]=="-20.125"
assert results[0]["temperature_capability"]["temp_max_c"]=="6.25"
profile=service.read(vehicle,"admin");assert profile["state"]=="READY"
requirements={"all_ranges_configured":True,"ranges_conflict":False,"common_min_c":"2","common_max_c":"8"}
compatible=temperature_preflight(requirements,profile)
assert compatible["planning_temperature_verified"] and compatible["feasible_min_c"]=="2" and compatible["feasible_max_c"]=="6.25"
assert not compatible["measurement_verified"] and not compatible["operational_admission"]
incompatible=temperature_preflight({**requirements,"common_min_c":"10","common_max_c":"20"},profile)
assert incompatible["status"]=="VEHICLE_RANGE_INCOMPATIBLE"
assert temperature_preflight({**requirements,"ranges_conflict":True},profile)["status"]=="SKU_RANGES_CONFLICT"
assert temperature_preflight(requirements,{**profile,"state":"BASE_CHANGED"})["status"]=="VEHICLE_PROFILE_UNCONFIRMED"
assert temperature_preflight(requirements,{**profile,"profile":{}})["status"]=="VEHICLE_RANGE_UNCONFIRMED"
try:service.configure({**body,"temp_max_c":"7"},"admin");raise AssertionError("Changed same-operation request accepted")
except Exception as exc:assert "OPERATION_CONFLICT"in str(exc),str(exc)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 trial={**body,"operation_id":"VEH.TEMP1152.ROLLBACK:"+tag,"expected_version":1,"temp_min_c":"2","temp_max_c":"8"}
 q.callproc("RRL_VEHICLE_PROFILE_API.configure",[json.dumps(trial),"admin",out]);assert read_oracle_json(out.getvalue())["version"]==2
 c.rollback()
 q.execute("select VERSION_NO from RRL_VEHICLE_PROFILE_HEAD where VEHICLE_ID=:v",v=vehicle);assert q.fetchone()==(1,)
 q.execute("select count(*)from RRL_VEHICLE_PROFILE_HIST where OPERATION_ID=:o",o=trial["operation_id"]);assert q.fetchone()==(0,)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
 q.execute("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-14-1149-vehicle-temperature-profile'");ledger=q.fetchone();assert ledger[1]=="APPLIED"
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_VEHICLE_PROFILE_HIST%'or upper(SQL_TEXT)like '%INTO RRL_VEHICLE_PROFILE_HEAD%')
 order by LAST_ACTIVE_TIME desc fetch first 3 rows only""");slow=[list(x)for x in q]
evidence={"vehicle_id":vehicle,"body":body,"result":results[0],"profile":profile,"planning":compatible,
          "incompatible":incompatible,"ledger":list(ledger),"slow_sql":slow,"protected_stock":[20,20],"state":"DONE"}
context.write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print(json.dumps({"case":"PASS1152","vehicle":vehicle,"version":1,"range":["-20.125","6.25"],"feasible":["2","6.25"],"slow_sql":slow,"stock":[20,20]}))
