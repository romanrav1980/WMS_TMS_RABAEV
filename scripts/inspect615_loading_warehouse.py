exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and NAME like 'RRL_%'
 and(upper(TEXT)like '%WARE_ID%WAREHOUSE%'or upper(TEXT)like '%WARE_ID%WARE_NO%'or upper(TEXT)like '%WARE_NO%WARE_ID%')
 and(NAME like '%LOAD%'or NAME like '%SHIPPING%')order by NAME,LINE fetch first 14 rows only""")
 print(json.dumps(q.fetchall()))
 q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_LOAD_CORE'and TYPE='PACKAGE BODY'and LINE between 74 and 77order by LINE")
 print(json.dumps(q.fetchall()))
