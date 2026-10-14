exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context519.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select distinct DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and ACTIVE_FLAG=1",op=ctx["load"])
 addresses=[r[0]for r in q];print("ADDR",json.dumps(addresses))
 for address in addresses:
  q.execute("select RECEIPT_MODE,POLICY_VERSION from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=:address",address=address);print("POLICY",json.dumps(q.fetchall()))
  q.execute("select count(*)from RRL_ADDR where ADDR=:address",address=address);print("MASTER",q.fetchone())
 q.execute("select count(*)from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:op",op=ctx["load"]);print("RECEIPTS",q.fetchone())
