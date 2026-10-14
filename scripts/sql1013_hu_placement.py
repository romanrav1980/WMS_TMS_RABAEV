exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1),substr(sql_text,1,200)
 from V$SQL where executions>0 and last_active_time>sysdate-1/24 and upper(sql_text)not like '%V$SQL%'and(
 upper(sql_text)like '%SELECT CL.TASK_ID,CL.CELL_SLOT_ID%'or
 upper(sql_text)like 'SELECT%FROM RRL_CUSTOMER_ORDER_FULFILLMENT WHERE LEGACY_SBORKA_PALLET_ID%')
 order by elapsed_time/nullif(executions,0)desc fetch first 8 rows only""")
 rows=q.fetchall();Path("tmp/sql1013_hu_placement.json").write_text(json.dumps(rows,indent=2,default=str),encoding="utf-8");print(json.dumps(rows,ensure_ascii=True,default=str))
