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

from .api.store_directory_routes import router as store_directory_router
from .contracts_store_directory import store_directory_service
from .infrastructure.store_directory import StoreDirectory


def build_store_directory() -> StoreDirectory:
    return StoreDirectory(OracleGateway())

from .api.warehouse_options_routes import router as warehouse_options_router, warehouse_options_service
from .infrastructure.warehouse_options import WarehouseOptions


def build_warehouse_options() -> WarehouseOptions:
    return WarehouseOptions(OracleGateway())

from .api.store_profile_routes import router as store_profile_router
from .contracts_store_profile import store_profile_service
from .infrastructure.store_profile import StoreProfile


def build_store_profile() -> StoreProfile:
    return StoreProfile(OracleGateway())
