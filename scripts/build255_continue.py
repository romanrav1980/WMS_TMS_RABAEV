from pathlib import Path
import json
s=Path("scripts/continue243.py").read_text(encoding="utf-8").replace("context243.json","context254.json").replace("IW243","IW255").replace("QI243","QI255").replace("READY243","READY255")
needle=' api("POST","/api/inventory/interwarehouse/release-custody",'
assert s.count(needle)==1
s=s.replace(needle,""" from app.modules.transport.public import TransportPreflight,generate_existing_operations
 coordination=TransportPreflight(OracleGateway())
 after_place=coordination.coordination(ctx["target_trip"],"admin")
 assert after_place["warehouse_placed_deliveries"]==1
 assert not any(x["code"]in("COORDINATION_WAREHOUSE_PLACEMENT_PENDING","COORDINATION_READY_PROMISE_AFTER_LOADING")for x in after_place["blockers"]),after_place
 assert any(x["code"]=="COORDINATION_ORIGINAL_ST_MEMBERS_REQUIRED"for x in after_place["blockers"])
"""+needle)
needle=' quality=api("GET","/api/outgoing-quality/"+st)'
assert s.count(needle)==1
s=s.replace(needle,""" # Actual membership invalidates old empty-TT approval; current source regeneration/approval required.
 changed=coordination.time_context(ctx["target_trip"],"admin")
 assert changed["approval_status"]=="SOURCE_CHANGED"
 generate_existing_operations(OracleGateway(),ctx["target_trip"],"admin")
 source=coordination.time_context(ctx["target_trip"],"admin")
 coordination.approve_time("TIME255.MEMBERS:"+tag,{"trip_id":ctx["target_trip"],"expected_version":source["version"],"source_hash":source["source_hash"],"time_zone":"UTC","reason":"Own255 original received member current loading plan"},"admin")
"""+needle)
needle=' api("POST",f"/api/transport/loading/{ctx[\'target_trip\']}/depart"'
a=s.index(needle)
s=s[:a]+""" complete=coordination.coordination(ctx["target_trip"],"admin")
 assert complete["warehouse_placed_deliveries"]==1 and complete["incoming"]["incoming_ready"]and complete["loading"]["all_members_physically_loaded"]
 # Loading changes source membership CONDITION; prior approval correctly becomes SOURCE_CHANGED.
 assert complete["time"]["approval_status"]=="SOURCE_CHANGED"
 assert any(x["code"]=="COORDINATION_TIME_NOT_CURRENT_APPROVED"for x in complete["blockers"])
 assert not complete["operational_admission"]and not complete["departure_authorized"]
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.get(base+f"/api/transport/preflight/trips/{ctx['target_trip']}/coordination")
  assert r.status_code==200 and r.json()["warehouse_placed_deliveries"]==1
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where sql_text like 'with candidates as(%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL_MS",q.fetchall())
 ctx["task255"]=task;ctx["st255"]=onward;Path("tmp/context254.json").write_text(json.dumps(ctx,ensure_ascii=True),encoding="utf-8")
 print("PASS255 original same3units6codes received/putaway/custody/nativeST assigned/QC/load only; placed0→1 clears predictionlate promise; current member approval invalidates after loading/sourcechanges honest BLOCKED/no admission/HTTP/protected20-20/target remains LOADED for next publish source fix",flush=True)
"""
print(json.dumps({"scripts/continue255.py":s},ensure_ascii=True))
