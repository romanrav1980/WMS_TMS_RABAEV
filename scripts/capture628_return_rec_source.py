exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RETURN_REC_CMD'and TYPE='PACKAGE BODY'order by LINE")
 value="create or replace "+"".join(x[0]for x in q)+"\n/\n"
 Path("tmp/628_return_rec_body.sql").write_text(value,encoding="utf-8")
print("628 read-only native source captured")
