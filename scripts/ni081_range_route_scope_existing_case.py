"""160 current approved210/draining207/closed209, route filter/read only, historical draft replay."""
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import build_range_proposal
from app.modules.inventory.contracts_range_proposal import RangeDraft
s=get_settings();ware=6667491;article="QNATIVED9A5C53B54"
body={"period_from":"2026-10-10","period_to_exclusive":"2026-10-11","declared_period_forecast":"44","forecast_base_uom":"EA",
 "declared_pallet_gross_weight_kg":"2","candidate_pick_route_id":146,
 "recommendation_costs":[{"pick_face_id":518,"pick_seconds_per_base":"1","replenish_seconds_per_pallet":"60","basis":"Own explicit route assumption"},
                         {"pick_face_id":519,"pick_seconds_per_base":"0.5","replenish_seconds_per_pallet":"150","basis":"Own explicit route assumption"}]}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware);stock=q.fetchone()
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  path=f"http://127.0.0.1:8088/api/inventory/slotting/warehouses/{ware}/articles/{article}/scenario"
  response=client.post(path,json=body);assert response.status_code==200,(response.status_code,response.text[:1500])
  data=response.json();rec=data["range_recommendation"]
  assert rec["candidate_pick_route_id"]==146 and rec["demand_and_old_range_scope"]=="WHOLE_ARTICLE_WAREHOUSE"
  assert rec["selected_faces"][0]["pick_face_id"]==518 and rec["recommended_total_face_count"]==3,rec
  current={row["pick_face_id"]:row for row in data["existing_range"]["cells"]}
  assert current[508]["range_mode"]=="DRAINING" and current[508]["new_replenishment_allowed"]is False,current
  assert current[519]["range_mode"]=="ACTIVE" and current[519]["new_replenishment_allowed"]is True,current
  assert data["scenario"]["old_stock_credit"]=="20"and data["scenario"]["nominal_additional_quantity"]=="24"
  invalid=client.post(path,json={**body,"candidate_pick_route_id":999999999})
  assert invalid.status_code==404 and "SLOTTING_CURRENT_CANDIDATE_ROUTE_REQUIRED"in invalid.text,(invalid.status_code,invalid.text[:1000])
  unscoped=client.post(path,json={key:value for key,value in body.items()if key!="candidate_pick_route_id"})
  assert unscoped.status_code==200 and unscoped.json()["scenario"]==data["scenario"]
 service=build_range_proposal(OracleGateway());op="RANGE157.SAVE2:52470cc7";original=service.get(ware,article,op,"admin")
 request=original["request"];command=RangeDraft(op,date.fromisoformat(request["period_from"]),date.fromisoformat(request["period_to_exclusive"]),
  Decimal(request["declared_period_forecast"]),request["forecast_base_uom"],Decimal(request["declared_pallet_gross_weight_kg"]),
  request["recommendation_costs"],request["expected_source_signature"],request["reason"])
 replay=service.save(ware,article,command,"admin")
 assert replay["status"]=="DRAFT"and original["status"]=="CANCELLED"
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware)
 assert q.fetchone()==stock==(20,20)
 print("PASS160 published route146 scopes newcandidates only/oldwholeWAREcredit20+whole24/current508draining519active/exact olddraft no-route replay unchanged/wrongroute404/no writesP20H20",flush=True)
