"""Reuse the already committed own actual load, exact API replay; no new shipment."""
import json,sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag="20a98330c0";op="FULL.HU.SHIP:"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 q=conn.cursor();q.execute("select CANONICAL_REQUEST,RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op)
 raw,result=q.fetchone()
 def decode(value):return value if isinstance(value,dict) else json.loads(value.read() if hasattr(value,"read") else value)
 command=decode(raw);saved=decode(result);metadata=command["metadata"];context=metadata["loading_context"]
 body={"operation_id":op,"identifier":command["source"]["uid"],**{key:value for key,value in metadata.items() if key!="loading_context"},**context}
 client=httpx.Client(auth=("admin","admin123"),timeout=30)
 response=client.post("http://127.0.0.1:8088/api/transport/loading/confirm",json=body)
 assert response.status_code==200,(response.status_code,response.text[:900]);assert response.json()==saved
 preview=client.get("http://127.0.0.1:8088/api/delivery/store-receipts/preview",params={"load_operation_id":op,"store_address":"STORE.QA:"+tag})
 assert preview.status_code==200,(preview.status_code,preview.text[:900]);data=preview.json()
 assert len(data["physical_boxes"])==1 and data["physical_boxes"][0]["gross_weight_kg"]=="2"
 assert data["shipping_weight_tolerance_kg"]=="1" and data["shipping_gross_weight_kg"]=="10"
 q.execute("select count(*) from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:op",op=op);assert q.fetchone()==(1,)
 print("PASS088 actual API exact loading context box replay, frozen box2KG/half tolerance1/source gross10, one original fact")
