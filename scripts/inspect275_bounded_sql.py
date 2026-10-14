exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),BUFFER_GETS/nullif(EXECUTIONS,0)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and (SQL_TEXT like '%SHIPPING_MEMBER_BOUNDED275%'or SQL_TEXT like '%SHIPPING_CELL_BOUNDED275%')order by last_active_time desc""")
 rows=q.fetchall();print("NEW_SQL",json.dumps(rows,ensure_ascii=True))
 for sql_id,executions,elapsed,buffers in rows:
  q.execute("select OPERATION,OPTIONS,OBJECT_NAME,CARDINALITY from V$SQL_PLAN where SQL_ID=:sql_id and OBJECT_NAME is not null order by ID",sql_id=sql_id)
  print("PLAN",sql_id,json.dumps(q.fetchall(),ensure_ascii=True))
 q.execute("select STATUS from USER_INDEXES where INDEX_NAME='RRL_ST_WARE_DAY_ID_I'");assert q.fetchone()==("VALID",)
