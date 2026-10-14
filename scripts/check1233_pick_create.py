exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_PICK_PLAN_CREATE_API','RRL_PICK_CREATE_OP_GUARD')")
 errors=q.fetchall();print(json.dumps({"errors":errors}));assert not errors
 q.execute("select PICK_PLAN_ID,STATUS from RRL_PICK_PLAN where CUSTOMER_ORDER_ID=2135")
 print(json.dumps({"plans":q.fetchall()}))
 q.execute("select count(*) from RRL_PICK_PLAN_CREATE_OP")
 print(json.dumps({"receipts":q.fetchone()[0]}))
