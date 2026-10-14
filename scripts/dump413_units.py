exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_UNIT_CORE'and TYPE='PACKAGE BODY'order by LINE")
 files['tmp/native413_unit.sql']='create or replace '+'\n'.join(x[0].rstrip('\r\n')for x in q)+'\n/\n'
print(json.dumps(files))
