exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1),substr(sql_text,1,220)
 from V$SQL where executions>0 and last_active_time>sysdate-1/24 and(
 upper(sql_text)like 'SELECT%RRL_CUSTOMER_ORDER_FULFILLMENT%LEGACY_SBORKA_PALLET_ID%'or
 upper(sql_text)like 'SELECT%RRL_RECEIPT_SLOT_CLAIM%HU_CASE_TASK_ID%'or
 upper(sql_text)like 'SELECT%RRL_SBORKA_PALLETS%FOR UPDATE%'or
 upper(sql_text)like 'SELECT%RRL_TT_HU_LOAD_ST%RRL_TT_HU_LOAD_FACT%')
 order by elapsed_time/nullif(executions,0)desc fetch first 10 rows only""")
 rows=q.fetchall();Path("tmp/sql1003_case_binding.json").write_text(json.dumps(rows,indent=2,default=str),encoding="utf-8")
 print(json.dumps(rows,ensure_ascii=True,default=str))
