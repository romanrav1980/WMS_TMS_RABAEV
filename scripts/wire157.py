import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");out[str(p)]=p.read_text(encoding="utf-8")+"""
from .contracts_range_proposal import RangeProposalPort,range_proposal_service
from .api.range_proposal_routes import router as range_proposal_router
from .infrastructure.range_proposal import RangeProposal

def build_range_proposal(gateway: Any) -> RangeProposalPort:
    return RangeProposal(gateway)
"""
p=Path("api/wms_api_server/app/main.py");out[str(p)]=p.read_text(encoding="utf-8")+"""
from .modules.inventory.public import range_proposal_router,range_proposal_service
from .range_proposal_composition import range_proposal
app.include_router(range_proposal_router)
app.dependency_overrides[range_proposal_service]=range_proposal
"""
print(json.dumps(out))
