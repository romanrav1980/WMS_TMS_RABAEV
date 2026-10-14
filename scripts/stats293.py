exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.cursor().callproc("DBMS_STATS.GATHER_TABLE_STATS",["RABAEV","RRL_INTERWARE_INCIDENT_CLOSE"])
ctx=json.loads(Path("tmp/context293.json").read_text(encoding="utf-8"))
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/inventory/interwarehouse/plans/"+ctx["plan_operation_id"]+"/decisions");assert r.status_code==200,r.text
exec(Path("scripts/read293sql.py").read_text(encoding="utf-8"))
