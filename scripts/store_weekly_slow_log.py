exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
p=Path('reports/retailcase/2026-10-13/codex/STORE_WEEKLY/native_sql.json');r=json.loads(p.read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select LOG_ID,to_char(CREATED_AT,'YYYY-MM-DD HH24:MI:SS'),ELAPSED_MS,API_PATH,dbms_lob.substr(SQL_TEXT,300,1)
 from RRL_SQL_SLOW_LOG where CREATED_AT>=systimestamp-interval'1'hour and(upper(dbms_lob.substr(SQL_TEXT,1000,1))like'%RRL_STORE_%'or upper(dbms_lob.substr(SQL_TEXT,1000,1))like'%RRL_TT_ROUTE_SCHEDULE%')order by CREATED_AT desc fetch first 5 rows only""");r['recent_matching_slow_log']=q.fetchall()
r['api_audit']='Not generated: bounded case called native owners directly, not HTTP. V$SQL and RRL_SQL_SLOW_LOG used.'
r['decision']='Retain indexed bounded material lookups: 200-address material measured75.233ms, profile query average0.041ms/window0.081ms; no evidence of dominant N+1 cost. Do not add speculative index. Revisit batchjoin at full200-stop route pilot if material dominates observedp95; ownertransport/root.'
p.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(r['recent_matching_slow_log']))
