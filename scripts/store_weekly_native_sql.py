exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
from time import perf_counter
from app.modules.platform.public import read_oracle_json
report={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select ADDR from RRL_ADDR where nvl(DELETED3,0)=0 order by ADDR fetch first 200 rows only');addresses=[r[0]for r in q]
 report['material_ms']={}
 for n in [1,8,200]:
  payload=json.dumps({'members':[{'address':a}for a in addresses[:n]]});out=q.var(oracledb.DB_TYPE_CLOB);start=perf_counter()
  q.callproc('RRL_STORE_WINDOW_RULES.material',[payload,out]);result=read_oracle_json(out.getvalue());assert len(result)==n
  report['material_ms'][str(n)]=round((perf_counter()-start)*1000,3)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)AVG_MS,BUFFER_GETS,substr(SQL_TEXT,1,650)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and LAST_ACTIVE_TIME>sysdate-1/24 and (SQL_TEXT like '%FROM RRL_STORE_PROFILE WHERE STORE_ADDR%'or SQL_TEXT like '%FROM RRL_STORE_RECEIVING_WINDOW WHERE STORE_ADDR%'or SQL_TEXT like '%RRL_ADDR_DISTANCE_MATRIX M ON%'or SQL_TEXT like '%FROM TABLE(:B1 )%')
 order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 12 rows only""");report['top_sql']=q.fetchall()
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_SQL_SLOW_LOG' order by COLUMN_ID");report['slow_log_columns']=[r[0]for r in q]
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_WINDOW_RULES','RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')and STATUS!='VALID'");report['changed_invalid']=q.fetchall()
Path('reports/retailcase/2026-10-13/codex/STORE_WEEKLY/native_sql.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(report))
