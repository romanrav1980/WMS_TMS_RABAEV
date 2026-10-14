exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.road_leg_estimate import road_leg_estimate,read_snapshot
from app.modules.transport.contracts_plan import TransportPlanError
import uuid
g=OracleGateway();depot="QA281:"+uuid.uuid4().hex[:8]
unknown=road_leg_estimate(g,33564,depot,24,"admin");assert unknown["status"]=="ROAD_DURATION_UNKNOWN"and unknown["drive_min"]is None
assert len(unknown["stops"])==1 and len(unknown["legs"])==2
try:road_leg_estimate(g,33564,depot,24,"SAP_FILE_GATEWAY")
except TransportPlanError as e:assert e.status==403
else:raise AssertionError("Gateway route bypass")
stop=unknown["stops"][0]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:
  for a,b,minutes in[(depot,stop,10.02),(stop,depot,20.02)]:
   q.execute("insert into RRL_ADDR_DISTANCE_MATRIX(FROM_ADDR,TO_ADDR,DISTANCE_KM,DURATION_MIN,DURATION_BASIS,SOURCE,UPDATED_AT)values(:from_address,:to_address,10,:duration_min,'ROAD_PROFILE_ESTIMATE','osrm',sysdate)",from_address=a,to_address=b,duration_min=minutes)
  ready=read_snapshot(q,33564,depot,24,"admin");assert ready["status"]=="ROAD_PROFILE_ESTIMATE_AVAILABLE"and ready["drive_min"]==11 and ready["drive_back_min"]==21
  q.execute("update RRL_ADDR_DISTANCE_MATRIX set DURATION_BASIS='SPEED_50_ESTIMATE'where FROM_ADDR=:depot",depot=depot)
  estimated=read_snapshot(q,33564,depot,24,"admin");assert estimated["status"]=="ROAD_DURATION_UNKNOWN"and estimated["drive_min"]is None
  q.execute("update RRL_ADDR_DISTANCE_MATRIX set DURATION_BASIS='ROAD_PROFILE_ESTIMATE',UPDATED_AT=sysdate-2 where FROM_ADDR=:depot",depot=depot)
  stale=read_snapshot(q,33564,depot,24,"admin");assert stale["status"]=="ROAD_DURATION_UNKNOWN"
 finally:c.rollback()
 q.execute("select count(*)from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR=:depot or TO_ADDR=:depot",depot=depot);assert q.fetchone()==(0,)
 q.execute("""select executions,round(elapsed_time/1000/nullif(executions,0),3),buffer_gets
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and executions>0 and SQL_TEXT not like '%V$SQL%'and dbms_lob.instr(SQL_FULLTEXT,'ROAD_LEGS_PK281')>0
 order by last_active_time desc fetch first 2 rows only""");print("SQL281_MS",q.fetchall())
print("PASS281 actual own33564 2members/1stop/2directedlegs current sourceV3; missing-speed-stale unknown, temporaryprofile10.02/20.02=>11/21minute inputs; allpairs rollback/currentgateway403/no route orquantity write; not realroad")
