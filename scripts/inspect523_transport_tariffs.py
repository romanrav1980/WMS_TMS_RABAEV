exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_SOURCE where NAME='RRL_UPDATE_PRICE'order by LINE")
 for r in q:print(json.dumps(r,ensure_ascii=True))
 q.execute("select LINE,TEXT from USER_SOURCE where NAME='TRANSPORT_TASK'and TYPE='PACKAGE BODY'order by LINE")
 rows=q.fetchall();starts=[i for i,(_,t)in enumerate(rows)if 'function stoim_tt'in t.lower()]
 for i in starts:
  for line,text in rows[i:i+100]:print(json.dumps([line,text],ensure_ascii=True))
 q.execute("select TABLE_NAME from USER_TABLES where TABLE_NAME like '%TARIF%'or TABLE_NAME like '%NORM%'or TABLE_NAME like '%PRICE%'order by TABLE_NAME")
 print("TABLES",json.dumps(q.fetchall()))
