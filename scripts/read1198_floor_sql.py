exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=json.loads(Path("tmp/context1194.json").read_text(encoding="utf-8"));assert d["state"]=="DEPARTED"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_FLOOR','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD','RRL_TRANSPORT_PLAN_RULES','RRL_LOAD_FLOOR_FACT_GUARD')");assert q.fetchall()==[]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,200)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and (upper(SQL_TEXT)like '%FROM RRL_TT_HU_LOAD_FACT L LEFT JOIN RRL_TT_LOAD_FLOOR_FACT%'or upper(SQL_TEXT)like '%FROM RRL_TARE_BOOK%'and upper(SQL_TEXT)like '%PLACE_KIND%')
 order by LAST_ACTIVE_TIME desc fetch first 6 rows only""");slow=[list(x)for x in q]
print(json.dumps({"native_errors":[],"slow_sql":slow,"trip":d["trip_id"],"typed_departure":d["departure_result"]["floor_at_departure"]}))
Path("tmp/read1198_floor_sql.json").write_text(json.dumps({"slow_sql":slow,"native_errors":[],"trip":d["trip_id"]},indent=2),encoding="utf-8")
