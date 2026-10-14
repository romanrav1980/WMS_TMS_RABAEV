import sys,json
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.domain.interwarehouse_timing import phase_timing
assert phase_timing("2026-10-11T10:00:00+03:00","2026-10-11T03:00:00-04:00","2026-10-11T08:00:00+00:00","UNLOADED")=={"state":"UNLOADED_ON_TIME","delay_seconds":"0"}
assert phase_timing("2026-10-11T10:00:00+03:00","2026-10-11T07:00:00.000001+00:00","2026-10-11T08:00:00+00:00","UNLOADED")=={"state":"UNLOADED_LATE","delay_seconds":"0.000001"}
assert phase_timing("2026-10-11T10:00:00+03:00",None,"2026-10-11T08:00:00+00:00","AT_GATE")=={"state":"OVERDUE","delay_seconds":"3600"}
s=get_settings();actor="WR23413508027ed"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,USER_GROUP from RUSERS where ID=:p",p=actor);secret,group=q.fetchone()
 with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
  r=h.post("http://127.0.0.1:8088/api/admin/rights/groups/"+group+"/rights",json={"right_name":"transport_dispatch_view","description":"Own238 aware phase queue view"});assert r.status_code==200,(r.status_code,r.text)
 with httpx.Client(auth=(actor,secret),timeout=35)as h:
  r=h.get("http://127.0.0.1:8088/api/inventory/interwarehouse/warehouses/51365792?include_completed=true");assert r.status_code==200,(r.status_code,r.text[:1600]);rows=r.json();row=next(x for x in rows if x["operation_id"]=="IW225.PLAN:13508027ed");assert row["arrival_timing"]["state"]=="UNLOADED_ON_TIME"and row["gate_timing"]["state"]=="AT_GATE_ON_TIME"
  assert row["placed_task_id"]==953 and row["observed_at"][-6]in"+-"
  r=h.get("http://127.0.0.1:8088/api/inventory/interwarehouse/warehouses/6667491");assert r.status_code==403,(r.status_code,r.text)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS238 actual current nonadmin queue/original225 unload-placement953 facts/same-snapshot aware timestamps/equal offset instant/one-microsecond lateness/pending overdue/foreignWARE403/no stock/protected20-20",flush=True)
