exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight,TransportPlanError
from app.modules.platform.public import read_oracle_json
import httpx
ctx=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"));trip=ctx["target_trip"];tag=ctx["tag"];g=OracleGateway();svc=TransportPreflight(g)
source=svc.time_context(trip,"admin");assert source["approval_status"]=="LEGACY_SOURCE_CONTRACT"
body={"trip_id":trip,"expected_version":source["version"],"source_hash":source["source_hash"],"time_zone":"UTC","reason":"Own256 explicit current loaded plan review"}
try:svc.approve_time("TIME256.DEFAULT:"+tag,body,"admin")
except TransportPlanError as exc:assert "TT_TIME_PHYSICAL_EXECUTION_FROZEN"in str(exc)
else:raise AssertionError("Implicit afterload approval permitted")
body["approval_phase"]="AFTER_LOADING_REVIEW"
decision=svc.approve_time("TIME256.REVIEW:"+tag,body,"admin")
assert decision["source_contract_version"]==2 and decision["plan_source"]["source_contract_version"]==2
assert decision["approval_phase"]=="AFTER_LOADING_REVIEW"
assert svc.approve_time("TIME256.REVIEW:"+tag,body,"admin")==decision
ready=svc.coordination(trip,"admin")
assert ready["status"]=="CURRENT_RECORDED_PHASES_COMPLETE"and not ready["blockers"],ready["blockers"]
assert not ready["operational_admission"]and not ready["departure_authorized"]
h=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
response=h.post(base+f"/api/transport/loading/{trip}/depart",json={"operation_id":"IW256.DEPART:"+tag})
assert response.status_code==200,(response.status_code,response.text[:1000])
final=svc.time_context(trip,"admin")
assert final["approval_status"]=="APPROVED"and final["source_hash"]==decision["source_hash"]
# Recorded execution fact updates do not change the material planned source.
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();arg=q.var(oracledb.DB_TYPE_CLOB);arg.setvalue(0,json.dumps({"fact_start":"2026-10-11 13:09","fact_end":"2026-10-11 13:24"}));out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_TT_OPERATION_PLAN_API.write_fact",[decision["operations"][0]["operation_id"],"admin",arg,out]);c.commit()
assert svc.time_context(trip,"admin")["source_hash"]==decision["source_hash"]
assert any(x["code"]=="COORDINATION_PLANNED_TRIP_REQUIRED"for x in svc.coordination(trip,"admin")["blockers"])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:uid and STOCK_STATUS='ISSUED'",uid=ctx["uid"]);assert q.fetchone()==(3,3)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL
 where sql_text like '%FROM RRL_SBORKA_PALLET_ROWS R WHERE EXISTS%TRANSTASK_ID%'
 and executions>0 order by last_active_time desc fetch first 3 rows only""");print("SQL_MS",q.fetchall())
ctx["time256"]=decision;ctx["load256"]="IW255.LOAD:"+tag;Path("tmp/context254.json").write_text(json.dumps(ctx,ensure_ascii=True),encoding="utf-8")
print("PASS256 original3units6codes unchanged/no unload bypass/explicit loaded review currentproof/defaultdenied/v2fullmaterialsnapshot/replay/native actual depart/thenOPSactualfact doesn'tinvalidateplan; 255 same snapshotphasecomplete before native departure/afterphaseblocked/protected20-20")
