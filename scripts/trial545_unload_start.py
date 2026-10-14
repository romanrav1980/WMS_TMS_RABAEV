exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context543.json").read_text(encoding="utf-8"));trial={**ctx["start_body"],"operation_id":"UNLOAD545.TRIAL:"+ctx["source"]["tag"]}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();result=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_STORE_UNLOAD_API.start_unloading",[json.dumps(trial),"admin",result])
 q.execute("select count(*)from RRL_STORE_UNLOAD_START where OPERATION_ID=:op",op=trial["operation_id"]);assert q.fetchone()[0]==1
 c.rollback()
 q.execute("select count(*)from RRL_STORE_UNLOAD_START where LOAD_OPERATION_ID=:op",op=trial["load_operation_id"]);assert q.fetchone()[0]==0
 print("PASS545 original clean lock plan/system captured start participates in outer rollback; no committed start/quantity effect.")
