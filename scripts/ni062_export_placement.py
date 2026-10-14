import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.modules.integrations.public import build_receipt_exporter
rows=build_receipt_exporter().export(Path("exchange/sap_receipts/outbox"),200)
print("Local gateway files published:",len(rows))
print("Placement823 exported:",any(r["event_id"]=="STORE_RETURN_PLACED:823" for r in rows))
