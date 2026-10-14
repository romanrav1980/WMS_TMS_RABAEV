exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_WORKLOAD_CONFIG_API','RRL_WORKLOAD_SCOPE_SITE_G')");errors=q.fetchall();print(json.dumps(errors));assert not errors
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'");invalid=q.fetchall();assert not invalid,invalid
 q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",password),timeout=30)as client:
 r=client.post("/api/transport/warehouse-forecast/warehouses/9807/view",json={"history_days":1,"horizon_days":1,"minimum_active_days":1,"include_current_day":True,"scope":"FULLPAL_DISPATCH"});r.raise_for_status()
 result=r.json();Path("tmp/forecast1332.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print(json.dumps({"status":result["status"],"series_count":len(result["series"]),"gaps":result["projection_gaps_at_least"],"labour":result["labour_estimate"],"own_series":[x for x in result["series"]if x["article"].startswith("QAUTOc0c2a00c0b")]}))
