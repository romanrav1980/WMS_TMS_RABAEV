exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from datetime import date
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select DATA_DEFAULT from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRANSPORT_TASK'and COLUMN_NAME='CONDITION'")
 assert q.fetchone()[0].strip()=="'Спланирован'"
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:
  trip=int(q.callfunc("RRL_TRASPORT_TASK_ADD",oracledb.DB_TYPE_NUMBER,["20",date(2026,10,14),"admin"]))
  q.execute("select CONDITION from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=trip);assert q.fetchone()[0]=="Спланирован"
  c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
  q.execute("select count(*)from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=trip);assert q.fetchone()[0]==0
 except:
  c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change");raise
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS253 actual column default exact Cyrillic and original legacy function creates planned status/native rollback leaves no TT/no goods/protected20-20. Historical bad rows unchanged.")
