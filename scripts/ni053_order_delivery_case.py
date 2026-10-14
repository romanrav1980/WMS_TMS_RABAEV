"""Actual existing orders: full acceptance and shortage credit, source history remains."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();client=httpx.Client(auth=("admin","admin123"),timeout=30)
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor()
 for tag,accepted,missing,expected in (("bea258a7dd","2","1","PARTIALLY_ACCEPTED"),("20a98330c0","3","0","RECEIVED_SHIPPED_VOLUME"),("22c5dc5ec4","3","0","ACCEPTED_WITH_OPEN_CASE")):
  op="FULL.HU.SHIP:"+tag
  q.execute("select to_number(json_value(RESOLVED_PLAN_JSON,'$.domain.shipments[0].domain.customer_order_id')) from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);order_id=int(q.fetchone()[0])
  q.execute("select STATUS,ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:id",id=order_id);original=q.fetchall()
  response=client.get(f"http://127.0.0.1:8088/api/customer-orders/{order_id}/delivery");assert response.status_code==200,(response.status_code,response.text[:1200]);data=response.json()
  assert data["delivery_status"]==expected,data
  assert len(data["quantities"])==1,data
  quantities=data["quantities"][0];assert quantities["shipped"]=="3" and quantities["accepted"]==accepted and quantities["missing"]==missing,quantities
  assert quantities["unreceived"]=="0" and data["unshipped_fulfillments"]==0
  assert data["delivery_scope"]=="SHIPPED_VOLUME" and not data["needs_owner_allocation"]
  q.execute("select STATUS,ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=:id",id=order_id);assert q.fetchall()==original
  q.execute("select STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=:id",id=order_id);assert q.fetchone()==("SHIPPED",3)
 print("PASS090 actual original orders: accepted2/missing1 partial, accepted3 full shipped volume, accepted3 with weight case; exact BASE/SKU, original demand/shipment unchanged")
