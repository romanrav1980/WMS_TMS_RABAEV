exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.shipping_register import read_snapshot
from datetime import date
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();cell="QIPcdbf4c0962";ware=13583852
 q.execute("select EXPEDITION_GROUP from RRL_CELLS where CELL=:cell_code and WARE_ID=:ware",cell_code=cell,ware=ware);old=q.fetchone()[0]
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where CELL=:cell_code",cell_code=cell);before=q.fetchone();assert before[0]>0
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("update RRL_CELLS set EXPEDITION_GROUP='QA275'where CELL=:cell_code and WARE_ID=:ware",cell_code=cell,ware=ware)
  report=read_snapshot(q,ware,date(2026,10,11),0,20)
  found=next(row for row in report["cells"]if row["cell"]==cell)
  assert found["positive_quantity_rows"]>0 and found["occupied"]and report["declared_cells_occupied"]
  assert not report["shipping_zone_empty_confirmed"]
 finally:c.rollback();q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select EXPEDITION_GROUP from RRL_CELLS where CELL=:cell_code",cell_code=cell);assert q.fetchone()==(old,)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where CELL=:cell_code",cell_code=cell);assert q.fetchone()==before
 q.execute("""select EXECUTIONS,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),BUFFER_GETS/nullif(EXECUTIONS,0)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and dbms_lob.instr(SQL_FULLTEXT,'SHIPPING_CELL_BOUNDED275')>0""");print("CELL_SQL_MS",q.fetchall())
print("PASS275 actual existing positive quantity in temporarily declaredownedcell/occupied notfalseempty/same transaction/no quantity changes/EXPEDITION_GROUP fullyrollback restored")
