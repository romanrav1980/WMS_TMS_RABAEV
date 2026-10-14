exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def context():
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TT_ROUTE_API.context",[33564,"admin",out]);return read_oracle_json(out.getvalue())
 before=context();assert before["source"]["source_contract_version"]==3 and len(before["source"]["members"])==2
 assert all("address"in m and "route_ordinal"in m and "st_date"in m for m in before["source"]["members"])
 c.rollback()
 member=before["source"]["members"][0]["id"]
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:
  q.execute("update RRL_SBORKA_PALLETS set ADDR=substr(ADDR,1,60)||':QA280'where ID=:pallet_id",pallet_id=member)
  changed=context();assert changed["source_hash"]!=before["source_hash"]and changed["route_status"]=="SOURCE_CHANGED"
 finally:
  c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
 restored=context();assert restored["source_hash"]==before["source_hash"];c.rollback()
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"])
 try:
  q.execute("update RRL_SBORKA_PALLETS set ORD=nvl(ORD,0)+10 where ID=:pallet_id",pallet_id=member)
  changed=context();assert changed["source_hash"]!=before["source_hash"]
 finally:
  c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
 assert context()["source_hash"]==before["source_hash"];c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT like '%ID,ST_NUMBER,WARE_ID,CONDITION,PALLET_UID,ADDR,STDATE,ORD%'
 order by last_active_time desc fetch first 2 rows only""");print("SQL280_MS",q.fetchall())
print("PASS280 actual own33564 current2planningmembers sourceV3 address/date/ordinal; address/order mutations stale oldroute, rollback restores exacthash; physical facts/P20H20 retained")
