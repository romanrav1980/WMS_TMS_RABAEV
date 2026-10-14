exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.transport.infrastructure.road_leg_estimate import read_snapshot,road_leg_estimate
from app.modules.transport.domain.vrp_distance_costs import distance_costs
from app.modules.transport.domain.vrp_travel_time import travel_times
from app.services.vrp_solver import VrpOrder
from app.oracle_gateway import OracleGateway
import httpx,uuid
unknown=road_leg_estimate(OracleGateway(),33564,"",24,"admin")
assert unknown["depot_basis"]=="WAREHOUSE_DEPOT_UNKNOWN"and unknown["drive_min"]is None
assert "WAREHOUSE_DEPOT_NOT_CONFIGURED"in unknown["source_issues"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ADDR from RRL_ADDR where nvl(DELETED3,0)=0 and SHIROTA between 1 and 89 and DOLGOTA between 1 and 179 group by ADDR having count(*)=1 order by ADDR fetch first 1 row only")
 addr=q.fetchone()[0];before=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_WARE_DEPOT_API.context",[9807,"admin",before])
 from app.modules.platform.public import read_oracle_json
 version=read_oracle_json(before.getvalue())["version"];c.rollback()
 body={"warehouse_id":9807,"expected_version":version,"depot_address":addr,"reason":"Изолированное чтение базы текущего рейса с полным откатом"}
 payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True))
 try:
  q.callproc("RRL_WARE_DEPOT_API.apply_setting",["QA286."+uuid.uuid4().hex[:12],"admin",payload,before])
  report=read_snapshot(q,33564,"",24,"admin")
  assert report["depot_address"]==addr and report["depot_basis"]=="CONFIGURED_WAREHOUSE_REFERENCE"
 finally:c.rollback()
orders=[VrpOrder("QA286","A",10,20,1,10,9807,None)]
matrix,depot=distance_costs(orders,{("H","A"):12,("A","H"):23},{"configured":True,"depot_address":"H","latitude":1,"longitude":2},lambda *args:999)
assert depot=="H"and matrix==[[0,23000],[12000,0]]
times,basis=travel_times(["A"],matrix,1,{("H","A"):17.01,("A","H"):31},"H")
assert times==[[0,31],[18,0]]and basis[1][0]=="ROAD_PROFILE_ESTIMATE"
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 r=client.get("http://127.0.0.1:8088/api/transport/preflight/trips/33564/road-legs")
 assert r.status_code==200 and r.json()["depot_basis"]=="WAREHOUSE_DEPOT_UNKNOWN",r.text
print("PASS286 owntrip configuredorigin same snapshot outerrollback, absentorigin UNKNOWN nozero, configured directedsolver12/23km and18/31minutes; HTTP default200 unknown/no qty")
