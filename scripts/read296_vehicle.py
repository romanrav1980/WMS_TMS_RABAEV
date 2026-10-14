exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_RULES'and TYPE='PACKAGE BODY'and LINE between 27 and 49 order by LINE")
 print("".join(r[0]for r in q))
 for number in[291,292]:
  ctx=json.loads(Path("tmp/context296_"+str(number)+".json").read_text());q.execute("select ADDR,TRANSPORT_TYPE,STOL,MAX_VEHICLE_TONS from RRL_ADDR where ADDR=:address_id",address_id=ctx["onward_result"]["final_address"]);print(number,q.fetchall())
