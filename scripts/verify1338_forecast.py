exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from uuid import uuid4
proof=json.loads(Path("tmp/result1334.json").read_text(encoding="utf-8"))
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
 q.execute("select count(*),max(VERSION_NO)from RRL_WORKLOAD_SCOPE_SITE where OPERATION_ID=:op",op=proof["submitted"]["operation_id"]);result["one_version"]=q.fetchone();assert result["one_version"]== (1,2)
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'");result["invalid"]=q.fetchall();assert not result["invalid"]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,200)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%RRL_WORKLOAD_SCOPE_SITE%'or SQL_TEXT like '%from json_table%RRL_WORKLOAD_NORM%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 6 rows only""");result["sql"]=q.fetchall()
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",password),timeout=20)as client:
 body=dict(proof["submitted"]);body["site_code"]="OTHER_SITE"
 r=client.post("/api/resources/workload/forecast-scopes",json=body);assert r.status_code==409 and "PAYLOAD_CONFLICT"in r.text
 result["conflict"]={"status":r.status_code,"body":r.json()}
 body=dict(proof["submitted"]);body["operation_id"]="FORECAST.STALE:"+uuid4().hex;body["expected_version"]=0
 r=client.post("/api/resources/workload/forecast-scopes",json=body);assert r.status_code==409 and "VERSION_CHANGED"in r.text
 result["stale"]={"status":r.status_code,"body":r.json()}
 r=client.get("/api/admin/slow-sql?limit=5&min_elapsed_ms=500");r.raise_for_status();result["slow"]=r.json()
Path("tmp/verify1338.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items()if k!="slow"},default=str))
