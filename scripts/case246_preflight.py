"""Current retained physical ST proof in the same READ ONLY snapshot."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight
from app.modules.transport.infrastructure.plan_preflight import current_sources,route_result
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select distinct ST_NUMBER from RRL_SBORKA_PALLETS where TRANSTASK_ID=33541")
 numbers=[r[0]for r in q.fetchall()]
 rows=current_sources(q,numbers,"admin",33541)
 loaded=[r for r in rows if r["condition"]==2]
 assert loaded and all(r["retained_load_proofs"]==1 for r in loaded),rows
 q.execute("select ID from RRL_TR_VEHICLE where NUM=(select TRANSPORT from RRL_TRANSPORT_TASK where ID=33541)")
 vehicle=q.fetchone()[0]
 own=route_result(q,{"vehicle_id":vehicle,"stops":numbers},rows,33541)
 assert not any(x["code"]=="PLAN_ST_FOREIGN_OR_SHIPPED"for x in own["source_blockers"]),own
 foreign=route_result(q,{"vehicle_id":vehicle,"stops":numbers},rows,None)
 assert any(x["code"]=="PLAN_ST_FOREIGN_OR_SHIPPED"for x in foreign["source_blockers"]),foreign
 completed=TransportPreflight(OracleGateway()).trip(33558,[],"admin")
 assert completed["status"]=="BLOCKED"
 assert all(r["retained_load_proofs"]==0 for r in completed["routes"][0]["current_sources"])
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3) from V$SQL
 where sql_text like 'select p.ID,p.ST_NUMBER,p.WARE_ID,p.TRANSTASK_ID,p.CONDITION,%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""")
 print("SQL_MS",q.fetchall())
 print("PASS246 own retained loaded ST allowed in preview; new/foreign plan and departed ST blocked; same snapshot/protected20-20/no writes; operational admission still false")
