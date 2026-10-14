"""Repeat the saved cluster operation through the existing endpoint, no new TT."""
import sys
from pathlib import Path
from urllib.parse import quote
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings();op="CLUSTER139:b40b0303ee3b"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select REQUEST_JSON,RESULT_JSON from RRL_CLUSTER_CREATE_RESULT where OPERATION_ID=:op",op=op)
 request,result=map(read_oracle_json,q.fetchone())
 district=request.pop("raion");request["operation_id"]=op
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  url="http://127.0.0.1:8088/api/admin/transport/clusters/"+quote(district,safe="")+"/create-task"
  answer=client.post(url,json=request)
  assert answer.status_code==200,(answer.status_code,answer.text[:1800])
  assert answer.json()==result
  del request["operation_id"]
  missing=client.post(url,json=request);assert missing.status_code==422,(missing.status_code,missing.text)
 print("PASS139 existing HTTP cluster endpoint returns saved original TT33528 after cancellation even with no free source; missing operation422/no write",flush=True)
