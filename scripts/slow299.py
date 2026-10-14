exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,90)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT not like '%OPT_DYN_SAMP%'
 and SQL_TEXT not like '%USER_TABLES%'and dbms_lob.instr(SQL_FULLTEXT,'RRL_INTERWARE_RECOVERY_APPROVAL')>0 order by ELAPSED_TIME desc fetch first 4 rows only""")
 rows=q.fetchall();Path("tmp/slow299.json").write_text(json.dumps(rows,indent=2),encoding="utf-8");print(json.dumps(rows))
