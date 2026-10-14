"""162 real existing planner save; controlled two inputs, no transport/stock mutation."""
import sys,json
from pathlib import Path
from datetime import date
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.services.transport_service import TransportService
from app.oracle_gateway import OracleGateway
gateway=OracleGateway(); service=TransportService(gateway)
# Deliberately synthetic input adapter; actual solver, matrix read, sequence and saved plan.
service.get_planner_orders=lambda **kwargs:[
 {"ST_NUMBER":"QA162.ARCHIVE:A","ADDR":"QA162.A","LAT":41.7,"LON":44.8,"PALLETS_COUNT":1,"WEIGHT_KG":10,"WARE_ID":6667491,
  "TIME_FROM":"06:00","TIME_TO":"08:00","TW_STRICT":1,"UNLOAD_NORM_MIN":40},
 {"ST_NUMBER":"QA162.ARCHIVE:B","ADDR":"QA162.B","LAT":41.71,"LON":44.81,"PALLETS_COUNT":1,"WEIGHT_KG":10,"WARE_ID":6667491,
  "TIME_FROM":"07:00","TIME_TO":"08:00","TW_STRICT":1,"UNLOAD_NORM_MIN":20},
]
service.list_vehicles=lambda **kwargs:[{"ID":162,"NUM":"QA162.TEST_ONLY","TR_TYPE":"5","PALLETS":4,"MAX_WEIGHT_KG":1000}]
result=service.solve_vrp(date(2026,10,11),ware_ids=[6667491],time_limit_s=1,solver="ortools",source="haversine")
assert result.plan_id and result.solver_used=="ortools-cvrptw" and not result.unassigned_sts
r=result.routes[0];assert r.schedule_status=="RELATIVE_SOLVER_SCHEDULE" and not r.operational_admission
assert next(s for s in r.stops if s.st_number.endswith(":A")).tw_from==0
row=gateway.fetch_all("select to_clob(PAYLOAD)PAYLOAD from RRL_PLANNER_PLANS where ID=:id",{"id":result.plan_id})[0]
saved=json.loads(row["payload"]);schedule=saved["routes"][0]["stop_schedule"]
assert len(schedule)==2 and all(x["arrival_min"]is not None for x in schedule)
assert {x["st_number"]:x["arrival_min"]for x in schedule}=={x.st_number:x.arrival_min for x in r.stops}
print("PASS162 existing solver+Oracle archive plan",result.plan_id,"two controlled inputs/06:00 zero retained/exact schedule; no apply/TT/ST/stock; not real order/HTTP acceptance")
