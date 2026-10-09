from ...oracle_gateway import OracleGateway
from .api.routes import router, policy_service
from .application.policy import ReceiptPolicyService
from .infrastructure.receipt_policy import ReceiptPolicyRepository


def build_policy_service() -> ReceiptPolicyService:
    return ReceiptPolicyService(ReceiptPolicyRepository(OracleGateway()))


__all__ = ["router", "policy_service", "build_policy_service"]
