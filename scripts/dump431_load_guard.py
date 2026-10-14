exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TT_HU_LOAD_FACT_GUARD'and TYPE='TRIGGER'order by LINE")
 body='create or replace '+'\n'.join(x[0].rstrip('\r\n')for x in q)+'\n/\n'
print(json.dumps({'tmp/native431_load_guard.sql':body}))
