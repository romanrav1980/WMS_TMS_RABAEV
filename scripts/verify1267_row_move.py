exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME in('RRL_ST_LAYOUT_READ','RRL_STOCK_ST_ROW_CMD','RRL_UPDATE_SBORKA_PALLET_ROWS2','RRL_STOCK_POSTING_API')order by NAME,SEQUENCE")
 errors=q.fetchall();print(json.dumps({"errors":errors}));assert not errors
 q.execute("select ID from RRL_SBORKA_PALLET_ROWS where PALLET_UID='OP_SAP_2135_1'and ARTICUL='QAUTOc0c2a00c0bB'")
 row_id=q.fetchone()[0]
 raw=q.callfunc("RRL_ST_LAYOUT_READ.snapshot",oracledb.DB_TYPE_CLOB,[2135,row_id,641508,"admin"])
 preview=json.loads(raw.read());Path("tmp/preview1267.json").write_text(json.dumps(preview,indent=2),encoding="utf-8")
 print(json.dumps(preview))
