exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=Path("db/migrations/2026-10-14_ni081_forecast_norm_scope");files={}
assert not (d/"checkpoint.json").exists()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for typ,file in [("PACKAGE","000_before_spec.sql"),("PACKAGE BODY","000_before_body.sql")]:
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_WORKLOAD_CONFIG_API'and TYPE=:typ order by LINE",typ=typ);source="".join(r[0]for r in q.fetchall());assert source
  files[str(d/file)]="create or replace "+source+"\n/\n"
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'")
 files[str(d/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-14-1328-forecast-norm-scope","target":"RABAEV/orcl","invalid_before":q.fetchall()},indent=2)
print(json.dumps(files,ensure_ascii=True))
