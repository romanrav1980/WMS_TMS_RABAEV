exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.infrastructure.interwarehouse_incoming import read_incoming_snapshot
import httpx
ctx=json.loads(Path("tmp/context291.json").read_text(encoding="utf-8"));plan=ctx["placement_result"];task=plan["task_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_ID=:task_id",task_id=task)
 uid,source,target,qty=q.fetchone();assert qty==1
 req={"contract_version":2,"operation_id":"IW291.PUT.DONE:"+ctx["tag"],"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],"metadata":{"fact_qty":"1","scanned_pallet":uid,"scanned_from_cell":source,"scanned_to_cell":target}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  result=read_oracle_json(out.getvalue());c.commit()
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=uid,cell_code=target);assert q.fetchone()==(1,0)
 c.rollback()
 current=read_incoming_snapshot(q,ctx["target_trip"],"admin")
 assert current["expected_quantities"][0]["quantity"]=="3"and not current["incoming_ready"]
 assert current["plans"][0]["received_quantity"]=="1"and current["plans"][0]["short_quantity"]=="2"and current["plans"][0]["receipt_complete"]==0
 q.execute("select RRL_INTERWARE_DEPART_GATE.promises(:trip_id)from dual",trip_id=ctx["target_trip"]);promises=read_oracle_json(q.fetchone()[0]);assert not promises[0]["physically_loaded"]
 q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",load_id=ctx["source_load"]);assert q.fetchone()==(None,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and
 (SQL_TEXT like '%RRL_INTERWARE_RECEIPT%'or SQL_TEXT like '%RRL_WMS_RECEIPT_UNIT%CURRENT_UID%')
 order by last_active_time desc fetch first 4 rows only""");print("SQL291_MS",q.fetchall())
 ctx["placement_complete_result"]=result;Path("tmp/context291.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("PASS291 actual originalPUT taskqty1 completes toexistingoutboundcell/P1H0; expected3/received1/short2/currentincomingnotready/departpromisefalse/custodyretained/P20H20; no missinggoods birth")
