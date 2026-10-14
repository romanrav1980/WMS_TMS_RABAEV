from ...oracle_gateway import OracleGateway
from .api.routes import router, policy_service
from .application.policy import ReceiptPolicyService
from .infrastructure.receipt_policy import ReceiptPolicyRepository


def build_policy_service() -> ReceiptPolicyService:
    return ReceiptPolicyService(ReceiptPolicyRepository(OracleGateway()))


__all__ = ["router", "policy_service", "build_policy_service", "published_cell_coverage"]

from .api.allocation_routes import router as allocation_router,allocation_policy_view,allocation_policy_edit,allocation_policy_service
from .infrastructure.allocation_policy import AllocationPolicy

def build_allocation_policy() -> AllocationPolicy:
    return AllocationPolicy(OracleGateway())

from .api.quality_weight_routes import router as quality_weight_router, quality_weight_service
from .infrastructure.quality_weight_policy import QualityWeightPolicy


def build_quality_weight_policy() -> QualityWeightPolicy:
    return QualityWeightPolicy(OracleGateway())

from .infrastructure.topology_coverage import published_cell_coverage
