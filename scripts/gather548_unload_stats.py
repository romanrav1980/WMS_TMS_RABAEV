exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_STORE_UNLOAD_START","RRL_STORE_UNLOAD_FACT"]:
  q.callproc("DBMS_STATS.GATHER_TABLE_STATS",[s.oracle_user.upper(),table])
 print("PASS548 only new unload-table statistics gathered; no business facts or quantities changed.")
