exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_REPL_CAPACITY'and TYPE='PACKAGE BODY'order by LINE")
 source="create or replace "+''.join(x[0]for x in q)+"\n/\n"
 Path("tmp/851_capacity_body.sql").write_text(source,encoding="utf-8")
 lines=source.splitlines()
 start=next(i for i,x in enumerate(lines)if "for r in(select rt.ARTICUL" in x)
 end=next(i for i in range(start+1,len(lines))if "for r in(select p.ARTICUL" in lines[i])
 print("\n".join(lines[max(0,start-3):end]))
