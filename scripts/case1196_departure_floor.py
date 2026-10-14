"""Continue retained actual1168 loaded lot; no new goods/warehouse/fleet fixture."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.transport_composition import build_transport_loading
from app.modules.platform.public import read_oracle_json
context_path=Path("tmp/context1194.json");d=json.loads(context_path.read_text(encoding="utf-8"))
assert d["state"]=="LOADED","Do not repeat departure fixture after completion"
loading=build_transport_loading();trip=d["trip_id"];tag=d["tag"];load_op=d["load_operation"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=10000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_TRIP_DEPART_CMD','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_POSTING_API','RRL_LOAD_THERMAL_FACT_GUARD')");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_TRIP_DEPART_CMD','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_POSTING_API','RRL_LOAD_THERMAL_FACT_GUARD')");objects=[list(x)for x in q];assert all(x[2]=="VALID"for x in objects)
 q.execute("select OBSERVED_C from RRL_TT_LOAD_THERMAL_FACT where LOAD_OPERATION_ID=:o",o=load_op);assert q.fetchone()==(3.125,)
for op,confirmation,expected in(("FLOOR1196.MISSING:"+tag,None,"DEPART_THERMAL_CURRENT_CONFIRMATION_REQUIRED"),
                                ("FLOOR1196.BAD:"+tag,{"origin":"MANUAL_AT_DEPARTURE","observed_c":"20","vehicle_profile_version":2,"observation_reference":"DEV1196.BAD:"+tag},"LOAD_THERMAL_OBSERVATION_INCOMPATIBLE")):
 try:loading.depart(op,trip,"admin",confirmation);raise AssertionError("Missing/bad departure temperature accepted")
 except Exception as exc:assert expected in str(exc),str(exc)
confirmation={"origin":"MANUAL_AT_DEPARTURE","observed_c":"3.750","vehicle_profile_version":2,"observation_reference":"DEV1196.NEW.MEASURE:"+tag}
trial_op="FLOOR1196.ROLLBACK:"+tag
trial={"contract_version":2,"operation_id":trial_op,"command_type":"TRIP_DEPART","actor":"admin","source":{"task_id":trip},"lines":[],"units":[],"metadata":{"temperature_confirmation":confirmation}}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=10000;q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(trial),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  result=read_oracle_json(out.getvalue());assert result["temperature_at_departure"]["observed_c"]=="3.75"
  assert result["floor_at_departure"]["status"]=="COMPATIBLE" and result["floor_at_departure"]["loaded_top_places"]==1
  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o",o=load_op);assert q.fetchone()==("DEPARTED",)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS,DEPARTURE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o",o=load_op);assert q.fetchone()==("LOADED",None)
 q.execute("select count(*)from RRL_TT_VEHICLE_SOURCE where TT_ID=:trip",trip=trip);assert q.fetchone()==(0,)
depart_op="FLOOR1196.DEPART:"+tag
d["departure_operation_id"]=depart_op;d["departure_confirmation"]=confirmation;d["state"]="DEPARTING"
context_path.write_text(json.dumps(d,indent=2),encoding="utf-8")
result=loading.depart(depart_op,trip,"admin",confirmation)
assert result==loading.depart(depart_op,trip,"admin",confirmation)
assert result["temperature_at_departure"]["origin"]=="MANUAL_AT_DEPARTURE"and result["temperature_at_departure"]["observed_c"]=="3.75"
assert result["stock_consumed_again"]is False
assert result["floor_at_departure"]["status"]=="COMPATIBLE" and result["floor_at_departure"]["counts"]==[{"pallet_type_id":1,"places":1}]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:o",o=depart_op);assert q.fetchone()==(0,)
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:cell",u=d["lot"],cell=d["ship_cell"]);assert q.fetchone()==(0,0)
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=5062399");assert q.fetchone()==(20,20)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT)like 'SELECT %'
 and upper(SQL_TEXT)not like '%V$SQL%'and (upper(SQL_TEXT)like '%MEMBER_SOURCE%'and upper(SQL_TEXT)like '%RRL_RECEIPT_SKU_RULE%'
 or upper(SQL_TEXT)like '%FROM RRL_TT_LOAD_THERMAL_FACT%')
 order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 3 rows only""")
 slow=[list(x)for x in q]
status=loading.status(trip,"admin")
assert status["temperature"]["departure_confirmation"]["observed_c"]=="3.75"
assert status["temperature"]["load_confirmations"][load_op]["confirmation"]["observed_c"]=="3.125"
d.update({"state":"DEPARTED","departure_result":result,"native_objects":objects,"slow_sql":slow,"current_status":status})
context_path.write_text(json.dumps(d,indent=2,default=str),encoding="utf-8")
print(json.dumps({"case":"PASS1196","trip":trip,"load_temperature":"3.125","departure_temperature":"3.75","repeat_stock":False,"protected":[20,20],"slow_sql":slow}))
