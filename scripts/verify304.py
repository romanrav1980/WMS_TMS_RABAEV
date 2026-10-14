exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table,constraint,event_col in [("RRL_INTERWARE_SHORTAGE_UNIT","RRL_IW_LOSS_EVENT_UNIT_PK","FACT_OPERATION_ID"),("RRL_INTERWARE_RECOVERY_UNIT","RRL_IW_REC_EVENT_UNIT_PK","RECOVERY_OPERATION_ID")]:
  q.execute("select COLUMN_NAME from USER_CONS_COLUMNS where TABLE_NAME=:tab and CONSTRAINT_NAME=:key_name order by POSITION",tab=table,key_name=constraint)
  assert [r[0]for r in q]==["PHYSICAL_UNIT_KEY",event_col]
  q.execute("select count(*),sum(BASE_QTY)from "+table);assert q.fetchone()==(2,2)
 try:
  q.execute("""insert into RRL_INTERWARE_SHORTAGE_UNIT(PHYSICAL_UNIT_KEY,FACT_OPERATION_ID,ORIGINAL_UID,UNIT_VERSION,BASE_QTY,BASE_UOM)
  select PHYSICAL_UNIT_KEY,FACT_OPERATION_ID,ORIGINAL_UID,UNIT_VERSION,BASE_QTY,BASE_UOM from RRL_INTERWARE_SHORTAGE_UNIT fetch first 1 rows only""")
 except oracledb.DatabaseError as exc:assert exc.args[0].code==20863,exc
 else:raise AssertionError("direct native journal forgery permitted")
 c.rollback()
 q.execute("""select count(*)from RRL_INTERWARE_SHORTAGE_UNIT booked where not exists(
 select 1 from RRL_INTERWARE_RECOVERY_UNIT recovered join RRL_STOCK_OPERATION restored on restored.OPERATION_ID=recovered.RECOVERY_OPERATION_ID
 where recovered.PHYSICAL_UNIT_KEY=booked.PHYSICAL_UNIT_KEY and recovered.LOSS_OPERATION_ID=booked.FACT_OPERATION_ID
 and restored.STATE='APPLIED'and restored.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER')""");assert q.fetchone()==(0,)
 q.execute("select NAME,TYPE,LINE from USER_ERRORS where NAME in('RRL_STOCK_INTERWARE_SHORT_CMD','RRL_IW_SHORT_UNIT_G')");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS304 event+unitPK enabled/old2+2qty histories preserved/currentactiveLoss0/directforgerydenied/allVALID/P20H20; secondphysicalcycle notclaimed")
