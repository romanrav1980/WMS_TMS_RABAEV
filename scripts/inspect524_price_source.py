exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_GET_TT_PRICE","RRL_GET_TT_PRICE_ID"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='FUNCTION'order by LINE",name=name)
  out[name]="".join(r[0]for r in q)
 q.execute("select TEXT from USER_SOURCE where NAME='TRANSPORT_TASK'and TYPE='PACKAGE BODY'order by LINE")
 v="".join(r[0]for r in q);a=v.lower().index("function stoim_pall_sb");b=v.lower().index("function stoim_tt",a);out["ST_PRICE"]=v[a:b]
 for name in ["RRL_TRANSPORT_PRICE","RRL_TRANSPORT_NORMS","RRL_TR_VEHICLE","RRL_STORE"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:name order by COLUMN_ID",name=name)
  out[name]=q.fetchall()
Path("tmp/price524.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in out.items()if k in ["RRL_GET_TT_PRICE","RRL_GET_TT_PRICE_ID","ST_PRICE"]}))
