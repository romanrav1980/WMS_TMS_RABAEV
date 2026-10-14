"""Inspect keys of immutable shipped provenance only; no writes."""
import json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for op in ("FULL.HU.SHIP:20a98330c0","FULL.HU.SHIP:bea258a7dd"):
  q.execute("select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);v=q.fetchone()[0]
  plan=v if isinstance(v,dict) else json.loads(v.read() if hasattr(v,"read") else v)
  domain=plan["domain"];print(op,"domain keys:",list(domain))
  for shipment in domain.get("shipments",[]):
   print("shipment keys:",list(shipment))
   for k,v in shipment.items():
    if isinstance(v,dict):
     print(k,"keys:",list(v))
     for k2,v2 in v.items():
      if isinstance(v2,dict):print(k2,"keys:",list(v2))
      elif isinstance(v2,list) and v2:print(k2,"first:",v2[0])
  q.execute("select TABLE_NAME from USER_TABLES where TABLE_NAME like 'RRL_CUSTOMER_ORDER%FULF%' order by TABLE_NAME")
  print("fulfillment tables:",[x[0] for x in q.fetchall()])
