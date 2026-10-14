exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_LOAD_BOX_WEIGHT'order by COLUMN_ID");print(json.dumps(q.fetchall()))
 q.execute("""select l.LOAD_OPERATION_ID,l.TT_ID,l.WARE_ID,b.BOX_UID,substr(l.COMPOSITION_JSON,1,250)
 from RRL_TT_HU_LOAD_FACT l join RRL_TT_LOAD_BOX_WEIGHT b on b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID
 where l.STATUS='DEPARTED'and b.BOX_UID like 'CASE:%'and not exists(select 1 from RRL_LOGISTICS_COST_LINE cost where cost.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID)
 order by l.LOADED_AT desc fetch first 8 rows only""");rows=q.fetchall()
 print(json.dumps([[x[0],x[1],x[2],x[3]]for x in rows]))
 Path("tmp/356_box_candidates.json").write_text(json.dumps([[x[0],x[1],x[2],x[3]]for x in rows]),encoding="utf-8")
