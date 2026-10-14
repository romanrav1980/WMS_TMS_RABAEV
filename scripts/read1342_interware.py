exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table,cols in [("RRL_INTERWARE_PLAN","OPERATION_ID,SOURCE_WARE_ID,TARGET_WARE_ID,SOURCE_TT_ID,TARGET_TT_ID"),("RRL_IW_GROUP_PLAN","OPERATION_ID,SOURCE_WARE_ID,TARGET_WARE_ID,SOURCE_TT_ID,TARGET_TT_ID")]:
  q.execute("select "+cols+" from "+table+" order by CREATED_AT desc fetch first 4 rows only");print(table,json.dumps(q.fetchall(),default=str))
