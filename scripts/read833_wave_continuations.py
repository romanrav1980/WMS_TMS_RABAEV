exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_WAVE_CMD' and TYPE='PACKAGE BODY' order by LINE")
 text="create or replace "+''.join(row[0] for row in q)+"\n/\n"
 Path("tmp/833_wave_body.sql").write_text(text,encoding="utf-8")
 lines=text.splitlines()
 for i,line in enumerate(lines):
  if any(x in line for x in ("if v_left>0 then","if p_plan.has('continuation')","procedure execute_target_supply")):
   print("\n".join(f"{j+1}: {lines[j]}" for j in range(max(0,i-3),min(len(lines),i+70))))
 q.execute("select COLUMN_NAME,DATA_TYPE,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' order by COLUMN_ID")
 print("RT_COLUMNS",q.fetchall())
