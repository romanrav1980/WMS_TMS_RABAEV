exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context1294.json").read_text(encoding="utf-8"));result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:a order by r.UID_POLETA,r.CELL",a=ctx["article"]);result["stock"]=q.fetchall()
 assert sum(x[2]for x in result["stock"])==12 and sum(x[3]for x in result["stock"])==5
 q.execute("select CURRENT_UID,count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:u group by CURRENT_UID order by CURRENT_UID",u=ctx["source"]);result["physical_units"]=q.fetchall();assert sorted(x[1]for x in result["physical_units"])==[5,7]
 q.execute("select SYSTEM_CODE,count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:u group by SYSTEM_CODE order by SYSTEM_CODE",u=ctx["source"]);result["codes"]=q.fetchall();assert result["codes"]==[("CRPT",12),("EGAIS",12)]
 q.execute("select STATE,count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o group by STATE",o=ctx["first_pick"]["request"]["operation_id"]);result["pick_operation"]=q.fetchall();assert result["pick_operation"]==[("APPLIED",1)]
 q.execute("select STATUS,PICKED_QTY,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:c",c=ctx["case"]);result["case"]=q.fetchone()
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,160)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%' and (SQL_TEXT like '%j.SCAN_INDEX,u.PHYSICAL_UNIT_KEY%'or SQL_TEXT like '%SERIALIZED_WEIGHT_BOXES%MARKING_REQUIRED%'or SQL_TEXT like '%SOURCE_DOC_TYPE=%PICK_WAVE%SOURCE_LINE_ID%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 5 rows only""");result["sql"]=q.fetchall()
Path("tmp/verify1298.json").write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
print(json.dumps(result,default=str))
