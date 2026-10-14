exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_UPDATE_PALLET_ROW2_SP_CALC'order by LINE")
 body="".join(x[0]for x in q).replace("\r","");Path("tmp/row_calc1264.sql").write_text(body,encoding="utf-8");print(body)
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE BODY'order by LINE");print("".join(x[0]for x in q)[:6000])
