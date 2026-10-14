exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3) AVG_MS,
 round(BUFFER_GETS/nullif(EXECUTIONS,0),2) AVG_BUFFERS,substr(SQL_TEXT,1,190) SQL_TEXT from V$SQL
 where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%INVALID_RECEIPT_ROWS%'or upper(SQL_TEXT)like '%SELECT COUNT(*)FROM RRL_SAP_SUPPLY_LINE L%'
 or upper(SQL_TEXT)like '%SELECT ID FROM RRL_PRIHOD_NAKLAD_ROWS WHERE ORDID%'
 or upper(SQL_TEXT)like '%COUNT(CASE WHEN POSTED_BASE_QTY%')
 order by LAST_ACTIVE_TIME desc fetch first 8 rows only""")
 result=[dict(zip([x[0].lower()for x in q.description],row))for row in q.fetchall()]
 q.execute("select INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME='RRL_SAP_PALLET_RECEIPT' order by INDEX_NAME,COLUMN_POSITION")
 indexes=q.fetchall()
 output={"queries":result,"receipt_indexes":indexes,"decision":"Keep bounded source<=1000 lines, indexed order/line receipt lookup and canonical legacy unique row; no new stock write/index needed. Author fixtures not production load proof."}
 Path("tmp/slow914.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
 print(json.dumps(output,ensure_ascii=True))
