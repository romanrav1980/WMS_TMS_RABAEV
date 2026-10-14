"""145 existing135 range/P20H20; no new stock or source dates."""
import sys
from pathlib import Path
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();path="http://127.0.0.1:8088/api/inventory/slotting/warehouses/6667491/articles/QNATIVED9A5C53B54/scenario"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");before=q.fetchone()
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post(path,json={"period_from":"2026-10-10","period_to_exclusive":"2026-10-11","declared_period_forecast":"100","forecast_base_uom":"EA"})
  assert r.status_code==200,(r.status_code,r.text[:2500])
  result=r.json();layout=result["existing_range"];assert layout["distinct_cell_count"]==1,layout
  row=layout["cells"][0];assert row["pick_face_id"]==508 and row["cell"]=="QGd9a5c53b54",row
  assert row["remaining_volume_base_quantity"] is not None and Decimal(row["remaining_volume_base_quantity"])==0,row
  assert "PHYSICAL_STOCK_OR_HARD_RESERVE"in row["withdrawal_blockers"]
  assert "UNFINISHED_CASE_LINES"in row["withdrawal_blockers"]
  assert not row["immediate_withdrawal_allowed"]and not row["physical_admission"]
  assert not result["apply_allowed"]and not layout["range_applied"]
  assert result["status"]=="PERIOD_ASSIGNMENT_REQUIRED"
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==before==(20,20)
 print("PASS145 existing face508 native volume budget0/current stock+unfinished CASE withdrawal blockers, no physical admission or range apply/P20H20 unchanged",flush=True)
