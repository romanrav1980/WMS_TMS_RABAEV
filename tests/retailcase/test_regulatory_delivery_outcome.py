"""Transmission ERROR must never be converted into delivery or legal acceptance."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import pytest
from app.modules.integrations.public import RegulatoryResponse,regulatory_delivery_decision

@pytest.mark.parametrize("status,http,expected",[("ERROR",503,False),("DONE",500,False),("STARTED",200,False),("DONE",202,True),("DONE",None,True),("DONE",True,False)])
def test_delivery_completion_is_not_inferred_from_any_response(status,http,expected):
 response=RegulatoryResponse(status,"PROVIDER_STATE",None,None,http,"{}",False)
 result=regulatory_delivery_decision(response)
 assert result.delivered is expected
 assert result.request_status==("DONE"if expected else"ERROR")
 if not expected:assert result.error_code and result.error_text
