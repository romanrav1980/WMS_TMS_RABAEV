exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,105)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(
 SQL_TEXT like 'SELECT LEGACY_SBORKA_PALLET_ID FROM (%RRL_INTERWARE_ONWARD_BIND%'
 or SQL_TEXT like 'SELECT COUNT(*)FROM RRL_INTERWARE_RECEIPT R JOIN RRL_INTERWARE_ONWARD_BIND%'
 or SQL_TEXT like 'SELECT LF.COMPOSITION_JSON,LF.ROOT_UID%')
 order by ELAPSED_TIME desc fetch first 10 rows only""");print("SQL312",json.dumps(q.fetchall()))
 ctx=json.loads(Path("tmp/context312.json").read_text(encoding="utf-8"))
 for _ in range(3):
  q.execute("""select b.ST_ID from RRL_INTERWARE_ONWARD_BIND b where b.WARE_ID=:ware_no and b.SOURCE_CELL=:source_cell and b.ROOT_UID=:lot_id
  and not exists(select 1 from RRL_INTERWARE_ONWARD_DISPATCH dispatched where dispatched.BIND_OPERATION_ID=b.OPERATION_ID)""",ware_no=ctx["source"]["target_warehouse"],source_cell=ctx["source"]["outbound"],lot_id=ctx["source"]["lot"])
  assert q.fetchall()==[]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT like 'select b.ST_ID from RRL_INTERWARE_ONWARD_BIND b where b.WARE_ID=:ware_no%'""");print("SQL313 scoped historicalexclude",q.fetchall())
 q.execute("select INDEX_NAME,STATUS from USER_INDEXES where INDEX_NAME in('RRL_IW_ONWARD_HU_SOURCE_IX','RRL_IW_REC_HU_SOURCE_IX')");assert all(r[1]=="VALID"for r in q)
