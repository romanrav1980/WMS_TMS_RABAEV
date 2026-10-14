exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select l.TT_ID,l.WARE_ID,l.LOAD_OPERATION_ID,
 count(b.BOX_UID),count(b.CASE_BOX_TASK_ID),min(t.STARTED_AT_INSTANT),max(t.STARTED_AT_INSTANT)
 from RRL_TT_HU_LOAD_FACT l join RRL_TT_LOAD_BOX_WEIGHT b on b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID
 left join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID
 where l.STATUS='DEPARTED'and not exists(select 1 from RRL_LOG_COST_SOURCE_CLAIM x where x.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID)
 group by l.TT_ID,l.WARE_ID,l.LOAD_OPERATION_ID having count(b.CASE_BOX_TASK_ID)>0
 order by l.TT_ID desc fetch first 8 rows only""")
 print(json.dumps(q.fetchall(),default=str))
