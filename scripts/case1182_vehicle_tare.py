"""Use retained owned vehicle10100; do not create stock, trips or another vehicle."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
from app.modules.transport.api.vehicle_profile_routes import VehicleProfileRequest
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from uuid import uuid4
context=Path("tmp/context1182.json");assert not context.exists(),"One metadata update already retained"
service=VehicleProfiles(OracleGateway());before=service.read(10100,"admin")
assert before["version"]==1 and before["state"]=="READY"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,TEXT from USER_ERRORS where NAME='RRL_VEHICLE_PROFILE_API'");assert q.fetchall()==[]
catalog=service.tare_types("admin");assert {1,3}.issubset({x["id"]for x in catalog})
old=json.loads(Path("tmp/context1152.json").read_text(encoding="utf-8"))["body"]
assert service.configure(old,"admin")["version"]==1,"Old exact receipt must survive upgrade"
variants=[{"code":"MIXED","limits":[{"pallet_type_id":1,"max_places":8},{"pallet_type_id":3,"max_places":4}]},
          {"code":"TROLLEYS","limits":[{"pallet_type_id":3,"max_places":20}]}]
body={**old,"operation_id":"VEH.TARE1182:"+uuid4().hex[:10],"expected_version":1,
      "floor_variants":variants,"reason":"Own retained dev vehicle: explicit tare loading variants","evidence_reference":"DEV1182:NO_REAL_FLEET_NORM"}
assert VehicleProfileRequest(**body).model_dump(mode="json",exclude_none=True)==body
context.write_text(json.dumps({"state":"PREPARED","vehicle_id":10100,"before":before,"body":body},indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 trial={**body,"operation_id":body["operation_id"]+".ROLLBACK"}
 q.callproc("RRL_VEHICLE_PROFILE_API.configure",[json.dumps(trial),"admin",out])
 assert read_oracle_json(out.getvalue())["floor_capacity"]["variants"]==variants
 c.rollback()
 q.execute("select VERSION_NO from RRL_VEHICLE_PROFILE_HEAD where VEHICLE_ID=10100");assert q.fetchone()==(1,)
 bad={**body,"operation_id":body["operation_id"]+".BAD","floor_variants":[{"code":"DUP","limits":[{"pallet_type_id":1,"max_places":8},{"pallet_type_id":1,"max_places":4}]}]}
 try:q.callproc("RRL_VEHICLE_PROFILE_API.configure",[json.dumps(bad),"admin",out]);raise AssertionError("Duplicate type accepted")
 except oracledb.DatabaseError as exc:assert "VEHICLE_TARE_TYPE_DUPLICATE"in str(exc)
 c.rollback()
result=service.configure(body,"admin");assert result["version"]==2 and result["floor_capacity"]["variants"]==variants
assert service.configure(body,"admin")==result
try:service.configure({**body,"floor_variants":variants[:1]},"admin");raise AssertionError("Changed payload accepted")
except Exception as exc:assert "OPERATION_CONFLICT"in str(exc)
after=service.read(10100,"admin");assert after["version"]==2
assert all(after["profile"]["temperature_capability"][k]==before["profile"]["temperature_capability"][k]for k in("temp_min_c","temp_max_c"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");stock=list(q.fetchone());assert stock==[20,20]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_VEHICLE_PROFILE_HIST%'or upper(SQL_TEXT)like '%FROM RRL_PALLET_TYPE WHERE PALLET_TYPE_ID%')
 order by LAST_ACTIVE_TIME desc fetch first 4 rows only""");slow=[list(x)for x in q]
evidence={"state":"DONE","vehicle_id":10100,"body":body,"result":result,"before":before,"after":after,"protected_stock":stock,"slow_sql":slow}
context.write_text(json.dumps(evidence,indent=2),encoding="utf-8")
print(json.dumps({"case":"PASS1182","vehicle":10100,"version":2,"variants":variants,"stock":stock,"slow_sql":slow}))
