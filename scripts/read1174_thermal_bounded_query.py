exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=json.loads(Path("tmp/context1168.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_THERMAL','RRL_STOCK_TRIP_DEPART_CMD','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_POSTING_API','RRL_LOAD_THERMAL_FACT_GUARD')");errors=q.fetchall();assert errors==[],errors
 # Exactly the deployed query shape. Existing one-member ST remains evidence,
 # without recreating stock or executing a second departure.
 sql="select /* CURRENT_LOAD_THERMAL_IN1173 */ distinct p.WARE_ID,r.ARTICUL,cfg.TEMP_MIN,cfg.TEMP_MAX from RRL_SBORKA_PALLETS p join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=p.WARE_ID and cfg.ARTICUL=r.ARTICUL where p.ID in (:id0) order by p.WARE_ID,r.ARTICUL fetch first 1001 rows only"
 q.execute(sql,id0=d["st_id"]);rows=q.fetchall();assert rows==[(d["warehouse_id"],d["article"],2,6)],rows
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT like 'select /* CURRENT_LOAD_THERMAL_IN1173 */%'order by LAST_ACTIVE_TIME desc fetch first 2 rows only");slow=[list(x)for x in q]
 result={"rows":[list(x)for x in rows],"slow_sql":slow,"native_errors":[],"read_only":True,"physical_rehearsal_after_query_rewrite":False}
 Path("tmp/read1174_thermal_bounded_query.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print(json.dumps({"case":"PASS1174","rows":len(rows),"slow_sql":slow,"scope":"deployed SELECT shape/current original ST, not new physical movement"}))
