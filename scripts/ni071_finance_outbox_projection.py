"""Bounded projection of original immutable dev finance facts, never a new charge."""
import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.modules.finance.infrastructure.finance_outbox import enqueue,expense_payload
gateway=OracleGateway();counts={}
sources=[
 ("WAREHOUSE_COST_RECOGNIZED","RRL_LOGISTICS_COST_RUN","MONETARY_RECOGNITION",""),
 ("EXTRA_EXPENSE_RECOGNIZED","RRL_LOGISTICS_EXP_DECISION","MONETARY_RECOGNITION","and d.PHASE='FINANCE' and d.OUTCOME='APPROVE'"),
 ("EXTRA_EXPENSE_REJECTED","RRL_LOGISTICS_EXP_DECISION","NO_POSTING","and d.PHASE='FINANCE' and d.OUTCOME='REJECT'"),
 ("EXTRA_EXPENSE_ALLOCATED","RRL_LOGISTICS_EXP_ALLOCATION","ALLOCATION_ONLY",""),
]
for event_type,table,semantics,condition in sources:
 with gateway.transaction("Project original immutable finance event") as cur:
  cur.execute("select d.OPERATION_ID,d.RESULT_JSON,to_char(sys_extract_utc(d.CREATED_AT),'YYYY-MM-DD\"T\"HH24:MI:SS.FF6\"Z\"')from "+table+" d where not exists(select 1 from RRL_SAP_RECEIPT_OUTBOX o where o.EVENT_ID='FIN:'||lower(rawtohex(standard_hash(:kind||':'||d.OPERATION_ID,'SHA256')))) "+condition+" and rownum<=200 order by d.OPERATION_ID for update skip locked",{"kind":event_type})
  rows=cur.fetchall()
  for op,result,created in rows:
   payload=read_oracle_json(result)
   if table=="RRL_LOGISTICS_EXP_DECISION":payload=expense_payload(cur,payload["expense_operation_id"],payload)
   payload["historical_fact_created_at_utc"]=created
   enqueue(cur,event_type,op,payload,semantics)
  counts[event_type]=len(rows)
print("Finance immutable projection",counts)
