exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_RECIPIENT_PALLET_POLICY','RRL_CASE_PALLET_TYPE_READ','RRL_STOCK_CASE_TYPE_CMD','RRL_STOCK_POSTING_API','RRL_TRANSPORT_PLAN_RULES','RRL_CASE_PALLET_TYPE_GUARD')order by NAME,SEQUENCE")
 errors=q.fetchall();print(json.dumps(errors));assert not errors,errors
