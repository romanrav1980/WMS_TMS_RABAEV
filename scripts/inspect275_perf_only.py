exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),BUFFER_GETS/nullif(EXECUTIONS,0)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and (dbms_lob.instr(SQL_FULLTEXT,'SHIPPING_MEMBER_BOUNDED275')>0 or dbms_lob.instr(SQL_FULLTEXT,'SHIPPING_CELL_BOUNDED275')>0)
 order by last_active_time desc""");print("NEW_SQL",json.dumps(q.fetchall(),ensure_ascii=True))
 q.execute("select STATUS from USER_INDEXES where INDEX_NAME='RRL_ST_WARE_DAY_ID_I'");assert q.fetchone()==("VALID",)
 q.execute("select r.CELL,c.WARE_ID from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where r.REMAIN>0 and c.CELL like 'Q%'and c.WARE_ID!=6667491 fetch first 1 rows only");print("OWN_POSITIVE",q.fetchall())
