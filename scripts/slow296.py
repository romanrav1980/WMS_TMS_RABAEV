exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,100)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT not like '%OPT_DYN_SAMP%'
 and (SQL_TEXT like 'SELECT COUNT(*)INTO%'or SQL_TEXT like 'SELECT COUNT(*)%'or SQL_TEXT like 'with candidates as(%')
 and(dbms_lob.instr(SQL_FULLTEXT,'RRL_INTERWARE_SHORTAGE_FACT')>0 or dbms_lob.instr(SQL_FULLTEXT,'RRL_INTERWARE_ONWARD_BIND')>0)
 order by ELAPSED_TIME desc fetch first 6 rows only""")
 rows=q.fetchall();Path("tmp/slow296.json").write_text(json.dumps(rows,indent=2),encoding="utf-8");print(json.dumps(rows))
