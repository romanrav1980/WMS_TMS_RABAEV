exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.loading_status import loading_status
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_HU_LOAD_CORE','RRL_LOAD_THERMAL_FACT_GUARD')order by NAME,TYPE,SEQUENCE")
 errors=[list(x)for x in q]
 q.execute("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_HU_LOAD_CORE','RRL_LOAD_THERMAL_FACT_GUARD')order by OBJECT_NAME,OBJECT_TYPE");objects=[list(x)for x in q]
 result={"errors":errors,"objects":objects}
 Path("tmp/verify1165_loading_thermal.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print(json.dumps(result,ensure_ascii=True));assert errors==[] and all(x[2]=="VALID"for x in objects)
r=loading_status(OracleGateway(),33571,"admin")
assert r["temperature"]["sensor_verified"]is False and not r["operational_admission"]
print(json.dumps({"status":"PASS1165","trip":33571,"temperature_profile":r["temperature"]["vehicle_profile"]["state"],"loads":len(r["physical_places"])}))
