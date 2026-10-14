import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.services.case_pick_service import CasePickService
from app.schemas import CasePickTaskActionRequest
CasePickService().start_task(1033,CasePickTaskActionRequest(actor="admin"))
print("Own1033 start works")
