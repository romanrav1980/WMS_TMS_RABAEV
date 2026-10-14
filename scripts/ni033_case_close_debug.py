import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import CaseCarrierCloseRequest,close_existing_case_carrier
from app.modules.resources.public import assert_case_task_access
print(close_existing_case_carrier(OracleGateway(),1030,CaseCarrierCloseRequest(operation_id="CASE.CLOSE167.DEBUG",expected_content_version=2,actor="admin",reason="Own closure preserves shipped state"),assert_case_task_access))
