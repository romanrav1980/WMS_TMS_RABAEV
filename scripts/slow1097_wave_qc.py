exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,420)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and
 (SQL_TEXT like '%ct.CONTENT_VERSION,ct.CURRENT_CELL,ct.SSCC%'or SQL_TEXT like 'SELECT%RRL_STOCK_QC_GATE.STATUS_JSON%'or SQL_TEXT like '%RRL_STOCK_WAVE_FINISH_CMD.SNAPSHOT_JSON%')
 order by ELAPSED_TIME desc fetch first 5 rows only""")
 rows=[list(x)for x in q]
 Path("tmp/slow1097_wave_qc.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
 print(json.dumps(rows,ensure_ascii=True))
