exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_GET_TT_PRICE'and(upper(TEXT)like '%HOUR%'or upper(TEXT)like '%RETURN%'or upper(TEXT)like '%PREMIO%')order by LINE")
 for line,value in q.fetchall():print(str(line)+":"+value.strip())
