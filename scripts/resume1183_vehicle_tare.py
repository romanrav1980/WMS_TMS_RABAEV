exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
from app.oracle_gateway import OracleGateway
p=Path("tmp/context1182.json");d=json.loads(p.read_text(encoding="utf-8"));assert d["state"]=="PREPARED"
service=VehicleProfiles(OracleGateway());after=service.read(d["vehicle_id"],"admin");result=service.configure(d["body"],"admin")
assert after["version"]==result["version"]==2 and result["floor_capacity"]["variants"]==d["body"]["floor_variants"]
for field in("temp_min_c","temp_max_c"):
 assert after["profile"]["temperature_capability"][field]==d["before"]["profile"]["temperature_capability"][field]
assert result["floor_capacity"]["evidence_reference"]==d["body"]["evidence_reference"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");stock=list(q.fetchone());assert stock==[20,20]
 q.execute("select NAME,TYPE,TEXT from USER_ERRORS where NAME='RRL_VEHICLE_PROFILE_API'");assert q.fetchall()==[]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_VEHICLE_PROFILE_HIST%'or upper(SQL_TEXT)like '%FROM RRL_PALLET_TYPE WHERE PALLET_TYPE_ID%')
 order by LAST_ACTIVE_TIME desc fetch first 4 rows only""");slow=[list(x)for x in q]
d.update(state="DONE",after=after,result=result,protected_stock=stock,slow_sql=slow,note="1182 assertion compared changed evidence reference; numeric range unchanged; resumed same committed profile without recreation")
p.write_text(json.dumps(d,indent=2),encoding="utf-8")
print(json.dumps({"case":"PASS1183","vehicle":d["vehicle_id"],"version":2,"stock":stock,"slow_sql":slow}))
