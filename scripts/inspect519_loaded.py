exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select l.LOAD_OPERATION_ID,l.TT_ID,l.WARE_ID,b.BOX_UID,l.STATUS
 from RRL_TT_HU_LOAD_FACT l join RRL_TT_LOAD_BOX_WEIGHT b on b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID
 join RRL_HU_PACK_CYCLE p on p.PARENT_UID=b.BOX_UID where l.STATUS='LOADED'
 order by l.LOADED_AT desc fetch first 2 rows only""")
 print(json.dumps(q.fetchall()))
