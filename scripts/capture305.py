exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_partial_recovery");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STOCK_IW_RECOVERY_PLAN","RRL_STOCK_IW_RECOVERY_REC"]:
  for kind in ["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind)
   source="".join(r[0]for r in q).replace(chr(13)," ").strip();assert source
   (d/("000_before_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
 for table in ["RRL_INTERWARE_RECOVERY_REQUEST","RRL_INTERWARE_RECOVERY_RECEIPT"]:
  q.execute("""select c.CONSTRAINT_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS col on col.CONSTRAINT_NAME=c.CONSTRAINT_NAME
   where c.TABLE_NAME=:tab and c.CONSTRAINT_TYPE='U'and col.COLUMN_NAME='LOSS_OPERATION_ID'
   and(select count(*)from USER_CONS_COLUMNS same_constraint where same_constraint.CONSTRAINT_NAME=c.CONSTRAINT_NAME)=1""",tab=table)
  rows=q.fetchall();assert len(rows)==1,rows
  q.execute("select CONSTRAINT_NAME,TABLE_NAME from USER_CONSTRAINTS where R_CONSTRAINT_NAME=:key_name",key_name=rows[0][0]);assert q.fetchall()==[]
  print(table,"lossUK",rows[0][0],"FK0")
print("Captured305 exact current recovery decision and physical owner")
