exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,LINE,TEXT from USER_SOURCE where NAME in('RRL_STORE_MARK_CORE','RRL_IW_AGG_SCAN','RRL_STOCK_UNIT_CORE')and TYPE='PACKAGE BODY'and lower(TEXT)like '%profile%'and lower(TEXT)like '%varchar2%'order by NAME,LINE fetch first 25 rows only")
 print(json.dumps(q.fetchall()))
