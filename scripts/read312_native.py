exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_INTERWARE_ONWARD_DISP_G","RRL_IW_REC_DISPATCH_G","RRL_STOCK_HU_LOAD_CORE"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg order by TYPE,LINE",pkg=name)
  source="".join(r[0]for r in q);Path("tmp/312_"+name.lower()+".sql").write_text(source,encoding="utf-8");print(name,len(source))
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_INTERWARE_ONWARD_DISPATCH','RRL_IW_RECOVERY_DISPATCH')");print("Dispatch guards",q.fetchall())
