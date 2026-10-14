exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_API'and TYPE='PACKAGE BODY'order by LINE")
 body="".join(row[0]for row in q);pos=body.find("v_requested_number:=v_requested.get_string")
 print(repr(body[pos:pos+500]))
 print(repr(body[body.find("v_requested_state number")-30:body.find("v_requested_state number")+100]))
