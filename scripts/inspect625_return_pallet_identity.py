exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and NAME='RRL_STOCK_STORE_RETURN_REC_CMD'
 and(upper(TEXT)like '%UID%'or upper(TEXT)like '%PALLET%')order by NAME,LINE fetch first 20 rows only""")
 print(json.dumps(q.fetchall()))
