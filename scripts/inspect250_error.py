exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
data=json.loads(Path("tmp/context250.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();a=q.var(oracledb.DB_TYPE_CLOB);a.setvalue(0,json.dumps(data["bodies"][0],sort_keys=True,separators=(",",":")));r=q.var(oracledb.DB_TYPE_CLOB)
 try:q.callproc("RRL_TT_TIME_API.approve",["TIME250.RACE:"+data["tag"]+".0","admin",a,r]);print("Unexpected approval");c.rollback()
 except oracledb.DatabaseError as exc:print("CODE",exc.args[0].code,"MESSAGE",exc.args[0].message);c.rollback()
