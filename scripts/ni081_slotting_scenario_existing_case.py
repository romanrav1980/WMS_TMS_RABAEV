"""Original135 metadata/stock only; temporarily date private QA headers and restore them."""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import stock_configuration_transaction
from app.oracle_gateway import OracleGateway
s=get_settings();client=httpx.Client(auth=("admin","admin123"),timeout=30)
path="http://127.0.0.1:8088/api/inventory/slotting/warehouses/6667491/articles/QNATIVED9A5C53B54/scenario"
query={"period_from":"2026-10-10","period_to_exclusive":"2026-10-11"}
def post(body,status=200):
 r=client.post(path,json=body);assert r.status_code==status,(r.status_code,r.text[:2500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");stock=q.fetchone()
 undated=post(query)
 assert undated["status"]=="PERIOD_ASSIGNMENT_REQUIRED"and Decimal(undated["undated_unpicked_quantity"])==20,undated
 q.execute("select CUSTOMER_ORDER_ID,SHIPMENT_DATE,CUSTOMER_ID,WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID in(1920,1921)order by CUSTOMER_ORDER_ID")
 headers=q.fetchall();assert len(headers)==2 and all(row[2]==-980702 and row[3]==6667491 for row in headers),headers
 try:
  with stock_configuration_transaction(OracleGateway(),"Own143 fixture calendar dates","admin","pick_topology_edit")as cursor:
   for identity,_day,_customer,_ware in headers:
    cursor.execute("update RRL_CUSTOMER_ORDER set SHIPMENT_DATE=:day where CUSTOMER_ORDER_ID=:id",day=date(2026,10,10),id=identity)
  current=post(query)
  assert Decimal(current["scenario"]["firm_unpicked_quantity"])==20,current
  assert Decimal(current["scenario"]["old_stock_credit"])==20,current
  declared=post({**query,"declared_period_forecast":"100","forecast_base_uom":"EA"})
  assert Decimal(declared["scenario"]["scenario_required_quantity"])==100,declared
  assert Decimal(declared["scenario"]["forecast_consumed_by_orders"])==20,declared
  assert not declared["apply_allowed"]and not declared["scenario"]["physical_layout_admission"]
  assert not current["scenario"]["zero_unobserved_demand_assumed"]
  wrong=post({**query,"declared_period_forecast":"100","forecast_base_uom":"BOX"},409)
  assert wrong["detail"]["code"]=="SLOTTING_FORECAST_BASE_MISMATCH"
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==stock==(20,20)
  print("PASS143 existing135 undated demand20 disclosed; own QA headers temporarily dated: firm20/HARD not doubled/old credit20, declared forecast100 consumes20=>100 not120/wrong BASE409; applyfalse/P20H20; original dates restored",flush=True)
 finally:
  with stock_configuration_transaction(OracleGateway(),"Restore own143 fixture dates","admin","pick_topology_edit")as cursor:
   for identity,day,_customer,_ware in headers:
    cursor.execute("update RRL_CUSTOMER_ORDER set SHIPMENT_DATE=:day where CUSTOMER_ORDER_ID=:id",day=day,id=identity)
