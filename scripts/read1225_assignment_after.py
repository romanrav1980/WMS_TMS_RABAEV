exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=Path("tmp/context1224.json");d=json.loads(ctx.read_text(encoding="utf-8"));assert d["state"]=="ASSIGNED_REPEATED"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PALLET_UID,TRANSTASK_ID,CONDITION from RRL_SBORKA_PALLETS where ST_NUMBER='SAP_2135'order by ID");rows=q.fetchall();assert len(rows)==2 and [r[:2]for r in rows]==[tuple(r[:2])for r in d["rows"]] and all(r[2]==33571 for r in rows),rows
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=9807");stock=q.fetchone();assert list(stock)==d["before_stock"]
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT like 'select t.ID,t.SHIPMENT_DATE,t.TRANSPORT,t.TEMP_REGION,t.DOCK,t.TEMP_WEIGHT,%' and EXECUTIONS>0 order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 3 rows only");slow=q.fetchall()
 d.update(state="ASSIGNED_VERIFIED",current_rows=rows,stock=list(stock),slow_sql=slow);ctx.write_text(json.dumps(d,indent=2),encoding="utf-8")
 print(json.dumps({"status":"PASS1225","trip":33571,"places":2,"old_ids_preserved":True,"stock":stock,"slow_sql":slow,"decision":"Existing 31day/keyset100 trip picker retained; no new index. Owner transport."}))
