exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ['RRL_INTERWARE_UNIT_SOURCE','RRL_INTERWARE_RECEIPT_GUARD','RRL_INTERWARE_CUSTODY_GUARD']:
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE in('PACKAGE BODY','TRIGGER') order by LINE",name=name)
  print(name+'\n'+''.join(x[0] for x in q))
