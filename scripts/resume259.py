exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,TransportPlanError
g=OracleGateway();svc=TransportPreflight(g);trip=33564
context=svc.route_context(trip,"admin");assert context["version"]==1
winner=context["last_input"]
body={"trip_id":trip,"expected_version":1,"source_hash":context["source_hash"],"drive_min":45,"drive_back_min":50,
 "source_reference":winner["source_reference"],"reason":winner["reason"]}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID from RRL_TT_OPERATIONS where TT_ID=:trip_id and OPERATION_CODE='DOCK_ASSIGN'",trip_id=trip);op_id=q.fetchone()[0]
 q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"]);q.execute("update RRL_TT_OPERATIONS set OPERATION_CODE='DRIVER_CHANGE'where ID=:op_id",op_id=op_id);q.callproc("RRL_STOCK_METADATA_TX.end_change");c.commit()
try:
 try:svc.apply_route_input("ROUTE259.LATE:33564",body,"admin")
 except TransportPlanError as e:assert e.status==409 and "OP_PLAN_CUSTOM_CHAIN_REVIEW_REQUIRED"in str(e),str(e)
 else:raise AssertionError("Custom chain bypass")
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select count(*)from RRL_TT_ROUTE_INPUT where TT_ID=:trip_id",trip_id=trip);assert q.fetchone()==(1,)
finally:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","transport_dispatch_edit"]);q.execute("update RRL_TT_OPERATIONS set OPERATION_CODE='DOCK_ASSIGN'where ID=:op_id",op_id=op_id);q.callproc("RRL_STOCK_METADATA_TX.end_change");c.commit()
time=svc.time_context(trip,"admin");assert time["approval_status"]!="APPROVED"
approved=svc.approve_time("TIME259:33564",{"trip_id":trip,"expected_version":time["version"],"source_hash":time["source_hash"],
 "time_zone":"Asia/Tbilisi","reason":"Own259 current original route45 plus return50 explicit timezone"},"admin")
preview=svc.trip_time(trip,"UTC","admin");assert preview["time_zone"]=="Asia/Tbilisi"and preview["driver_rest"]["drive_min"]=="95.0"
assert not preview["driver_rest"]["unknown_intervals"]and not preview["operational_admission"]
try:svc.route_context(trip,"WR23413508027ed")
except TransportPlanError as e:assert e.status==403
else:raise AssertionError("Foreign emptytrip")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:q.execute("delete from RRL_TT_ROUTE_INPUT where TT_ID=:trip_id",trip_id=trip)
 except oracledb.DatabaseError as e:assert getattr(e.args[0],"code",0)==20863
 else:raise AssertionError("History deletion")
 c.rollback()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like '%FROM RRL_TT_ROUTE_INPUT WHERE TT_ID=%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
Path("tmp/context259.json").write_text(json.dumps({"trip_id":trip,"route_input":winner,"time":approved},ensure_ascii=True),encoding="utf-8")
print("PASS259 resumed own33564/currentjournal1/customchainlatefailure rollback source setup restored/no dirtyTXbypass/timeV2approved/95min/foreign403/historyguard/protected20-20. Initial rollback/concurrentHTTP200-409/replay/payload/IDs already passed; no repeat publication.")
