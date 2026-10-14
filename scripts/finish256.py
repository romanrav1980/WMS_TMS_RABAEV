exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));svc=TransportPreflight(OracleGateway())
state=svc.time_context(ctx["target_trip"],"admin");decision=state["last_approval"]
assert state["approval_status"]=="APPROVED"and decision["approval_phase"]=="AFTER_LOADING_REVIEW"
assert any(x["code"]=="COORDINATION_PLANNED_TRIP_REQUIRED"for x in svc.coordination(ctx["target_trip"],"admin")["blockers"])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and STOCK_STATUS='ISSUED'",lot_id=ctx["uid"]);assert q.fetchone()==(3,3)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL
 where sql_text like '%FROM RRL_SBORKA_PALLET_ROWS R WHERE EXISTS%TRANSTASK_ID%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""");print("SQL_MS",q.fetchall())
ctx["time256"]=decision;ctx["load256"]="IW255.LOAD:"+ctx["tag"];Path("tmp/context254.json").write_text(json.dumps(ctx,ensure_ascii=True),encoding="utf-8")
print("PASS256 final same3 original units ISSUED after existing native depart33570; materialV2 approval remainscurrent including recordedactualOPSfact; afterdepart coordinatorphase blocked/protected20-20/no newbirth or unloadbypass. Previous helper allphase assertionspassed then final reservedUIDbind corrected.")
