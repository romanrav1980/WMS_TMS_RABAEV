exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.delivery.infrastructure.return_progress import return_progress
result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 result["not_authorized_progress"]=return_progress(q,["REUSE643.APPROVE:dc1889623c"],"OWN1306_DRIVER");assert result["not_authorized_progress"]=={}
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT like '%RETURN_PROGRESS1355%'order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 4 rows only""");result["sql"]=q.fetchall()
print(json.dumps(result,default=str))
Path("tmp/verify1362.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
