"""Old canonical receipt replay and current logistics act dossier."""
import json,sys
from pathlib import Path
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();client=httpx.Client(auth=("admin","admin123"),timeout=25);base="http://127.0.0.1:8088/api/delivery/store-receipts"
def decode(raw):return raw if isinstance(raw,dict) else json.loads(raw.read() if hasattr(raw,"read") else raw)
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor()
 for op in ("STORE.RECEIPT:04633c677f","STORE.RECEIPT:bea258a7dd"):
  q.execute("select CANONICAL_REQUEST,RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);raw,saved=q.fetchone();command=decode(raw)
  body={"operation_id":op,**command["source"],**command["metadata"]}
  response=client.post(base+"/confirm",json=body);assert response.status_code==200,(response.status_code,response.text[:900]);assert response.json()==decode(saved)
 q.execute("select c.CASE_ID from RRL_STORE_DISCREPANCY_CASE c join RRL_STORE_RECEIPT_WEIGHT w on w.OPERATION_ID=c.CASE_ID where w.ACT_CONFIRMED=1 order by c.CREATED_AT desc fetch first 1 row only");case=q.fetchone()[0]
 response=client.get(base+"/cases/"+case);assert response.status_code==200,(response.status_code,response.text[:900]);dossier=response.json()
 assert dossier["weight"]["delta_kg"]=="1.000000001" and dossier["weight"]["tolerance_kg"]=="1"
 assert dossier["lines"][0]["accepted_base_qty"]=="3" and dossier["obligations"]==[]
 assert dossier["status"]=="OPEN" and not dossier["return_approved"] and not dossier["warehouse_stock_restored"]
 print("PASS089 old083/full+086/discrepancy exact canonical replay after new omitted defaults; current representative weight act dossier exact strings/no fabricated quantity loss")
