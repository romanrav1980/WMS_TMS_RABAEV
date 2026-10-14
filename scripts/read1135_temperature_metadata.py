exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where COLUMN_NAME like '%TEMPERATURE%'or COLUMN_NAME like '%TEMP_MIN%'or COLUMN_NAME like '%TEMP_MAX%'or COLUMN_NAME like '%COLD%'order by TABLE_NAME,COLUMN_ID fetch first 101 rows only")
 r={"existing_temperature_columns":[list(x)for x in q]}
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,140)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%RETAINED_LOAD_PROOFS%'or SQL_TEXT like '%RRL_TRANSPORT_PLAN_RULES.check_vehicle%')order by last_active_time desc fetch first 3 rows only")
 r["preflight_slow_sql"]=[list(x)for x in q]
 Path("tmp/read1135_temperature_metadata.json").write_text(json.dumps(r,indent=2),encoding="utf-8");print(json.dumps(r,ensure_ascii=True))
