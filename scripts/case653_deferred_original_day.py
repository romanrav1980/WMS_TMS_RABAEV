exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from datetime import date
from app.modules.finance.infrastructure.shipping_register import read_snapshot
ctx=json.loads(Path("tmp/context276.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select WARE_ID,json_value(RESULT_JSON,'$.original_shipping_date'),json_value(RESULT_JSON,'$.target_shipping_date')from RRL_ST_DEFER_DECISION where OPERATION_ID=:op",op=ctx["operation"]);ware,old_day,new_day=q.fetchone();assert old_day!=new_day
 day=date.fromisoformat(old_day)
 q.execute("select ID,STDATE from RRL_SBORKA_PALLETS where ST_NUMBER=:st and WARE_ID=:ware order by ID",st=ctx["st"],ware=ware);before=q.fetchall();assert len(before)==2
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("update RRL_SBORKA_PALLETS set STDATE=null where ST_NUMBER=:st and WARE_ID=:ware",st=ctx["st"],ware=ware)
  q.execute("select count(*)from RRL_SBORKA_PALLETS p join RRL_TRANSPORT_TASK t on t.ID=p.TRANSTASK_ID where p.ST_NUMBER=:st and p.WARE_ID=:ware and t.SHIPMENT_DATE>=:day_start and t.SHIPMENT_DATE<:day_end",st=ctx["st"],ware=ware,day_start=day,day_end=date.fromisoformat(new_day));assert q.fetchone()[0]==0
  full=read_snapshot(q,ware,day,0,20);rows=[r for r in full["rows"]if r["st_number"]==ctx["st"]]
  assert len(rows)==2 and all(r["trip_id"]==ctx["target_trip"]and r["deferral_version"]==1 for r in rows)
  first=read_snapshot(q,ware,day,0,1);assert first["has_more"]
  second=read_snapshot(q,ware,day,first["next_after_id"],1)
  assert {first["rows"][0]["st_pallet_id"],second["rows"][0]["st_pallet_id"]}=={r[0]for r in before}
  c.rollback()
 finally:c.rollback();q.callproc("RRL_STOCK_CONFIG_API.end_change")
 q.execute("select ID,STDATE from RRL_SBORKA_PALLETS where ST_NUMBER=:st and WARE_ID=:ware order by ID",st=ctx["st"],ware=ware);assert before==q.fetchall()
 q.execute("select INDEX_NAME,STATUS from USER_INDEXES where INDEX_NAME='RRL_ST_DEFER_ORIG_DAY_I'");assert q.fetchone()==("RRL_ST_DEFER_ORIG_DAY_I","VALID")
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and dbms_lob.instr(SQL_FULLTEXT,'original_day')>0 and dbms_lob.instr(SQL_FULLTEXT,'SHIPPING_MEMBER_BOUNDED275')>0 and upper(SQL_TEXT)not like '%V$SQL%'order by LAST_ACTIVE_TIME desc fetch first 2 rows only")
 print("SQL653",json.dumps(q.fetchall()))
print("PASS653 legacyNULL-date original day includes2retained deferredmembers/currentnewtrip/reasonversion1/cursor stable/outer rollback restores source; no old factory/no qty")
