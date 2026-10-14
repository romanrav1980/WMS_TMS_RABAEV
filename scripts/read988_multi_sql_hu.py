exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where(sql_text like 'SELECT%RRL_CASE_CARRIER_LOT%'or sql_text like 'SELECT%RRL_SBORKA_PALLETS%ST_NUMBER%')and executions>0 order by last_active_time desc fetch first 7 rows only")
 evidence=q.fetchall();Path("tmp/multi988_sql.json").write_text(json.dumps(evidence),encoding="utf-8");print("SQL",evidence)
 for name in("RRL_STOCK_HU_CASE_CORE","RRL_STOCK_HU_CORE"):
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name)
  body="".join(r[0]for r in q);Path("tmp/988_"+name.lower()+".sql").write_text(body,encoding="utf-8");print(name,len(body))
 data=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));print("CASES",data.get("cases"),"TASKS",data.get("moves"))
