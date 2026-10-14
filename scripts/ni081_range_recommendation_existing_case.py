"""156 original face508 + rollback-only metadata alternatives, no stock or published range change."""
import sys
from pathlib import Path
from decimal import Decimal
from uuid import uuid4
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.infrastructure.slotting_candidates import recommendation_sources
from app.modules.inventory.infrastructure.slotting_layout import range_capacity
from app.modules.inventory.domain.slotting_demand import quantity_scenario
s=get_settings();tag=uuid4().hex[:8];ware=6667491;article="QNATIVED9A5C53B54"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware);stock=q.fetchone()
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","pick_topology_edit"])
 try:
  def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
  route=seq("RRL_PICK_ROUTE_SQ")
  q.execute("insert into RRL_PICK_ROUTE(PICK_ROUTE_ID,WARE_ID,ROUTE_CODE,ROUTE_NAME,STATUS,ACTIVE)values(:id,:ware,:code,'Own rollback-only cost route','PUBLISHED',1)",id=route,ware=ware,code="Q156"+tag)
  faces=[]
  for n,volume in enumerate(["1.2","1.2","0.5"]):
   cell="Q156"+tag+str(n);face=seq("RRL_PICK_FACE_SQ");rc=seq("RRL_PICK_ROUTE_CELL_SQ");faces.append(face)
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM)values(:cell,:ware,0,0,0,1,0)",cell=cell,ware=ware)
   q.execute("insert into RRL_PICK_ROUTE_CELL(PICK_ROUTE_CELL_ID,PICK_ROUTE_ID,WARE_ID,CELL_CODE,PICK_SEQUENCE,ACTIVE)values(:id,:route,:ware,:cell,:n,1)",id=rc,route=route,ware=ware,cell=cell,n=n+1)
   q.execute("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,MAX_WEIGHT,PICK_FACE_TYPE,ALLOW_DYNAMIC_ASSIGNMENT,PICK_ROUTE_ID,PICK_ROUTE_CELL_ID,CREATED_BY)values(:id,:ware,:cell,:volume,200,'DYNAMIC',1,:route,:rc,'admin')",id=face,ware=ware,cell=cell,volume=Decimal(volume),route=route,rc=rc)
  scenario=quantity_scenario(Decimal(150),None,Decimal(50),Decimal(0),Decimal(100))
  layout=range_capacity(q,ware,article,scenario["nominal_additional_quantity"])
  costs=[{"pick_face_id":faces[0],"pick_seconds_per_base":"1","replenish_seconds_per_pallet":"60","basis":"Own declared route normative"},
         {"pick_face_id":faces[1],"pick_seconds_per_base":"0.5","replenish_seconds_per_pallet":"150","basis":"Own declared route normative"}]
  result=recommendation_sources(q,ware,article,scenario,layout,Decimal(120),costs)
  assert result["status"]=="NOMINAL_RECOMMENDATION",result
  assert result["required_additional_whole_pallets"]==1 and result["recommended_total_face_count"]==2,result
  assert result["selected_faces"][0]["pick_face_id"]==faces[0] and result["estimated_total_additional_seconds"]=="160",result
  small=next(row for row in result["candidates"]if row["pick_face_id"]==faces[2])
  assert "WHOLE_PALLET_VOLUME_INSUFFICIENT"in small["refusal_reasons"]
  partial=recommendation_sources(q,ware,article,scenario,layout,Decimal(120),costs[:1])
  assert partial["status"]=="COST_ASSUMPTIONS_REQUIRED"and not partial["selected_faces"]
  unknown=recommendation_sources(q,ware,article,scenario,layout,None,costs)
  assert not unknown["selected_faces"] and not unknown["physical_admission"]
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware)
  assert q.fetchone()==stock==(20,20)
  assert not result["applied"] and result["old_faces_preserved"]
  print("PASS156 actual original508 + own rollback metadata: need150/old50/addwhole100 -> total2faces; cost160beats200; too-smallface/refused, missingcost refuses selection, unknownweight no admission/P20H20 unchanged",flush=True)
 finally:
  q.callproc("RRL_STOCK_CONFIG_API.end_change");c.rollback()
 # Real existing HTTP scenario has no persistent QA candidates.
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  r=client.post(f"http://127.0.0.1:8088/api/inventory/slotting/warehouses/{ware}/articles/{article}/scenario",json={
    "period_from":"2026-10-10","period_to_exclusive":"2026-10-11","declared_period_forecast":"150","forecast_base_uom":"EA","declared_pallet_gross_weight_kg":"120"})
  assert r.status_code==200,(r.status_code,r.text[:1000])
  body=r.json();assert "range_recommendation"in body and not body["apply_allowed"],body
