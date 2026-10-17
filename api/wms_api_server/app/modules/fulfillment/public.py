from typing import Any, Callable
from .application.wave_launch_continuation import run_wave_launch
from .infrastructure.wave_continuation import WaveContinuation
from .infrastructure.wave_launch_adapter import launch_steps, post_frozen_sources
from .infrastructure.wave_launch_receipt import read_launch_receipt
from ...oracle_gateway import OracleGateway
from .api.store_order_routes import router, store_order_service, preparation_service
from .infrastructure.store_orders import StoreOrders
from .infrastructure.legacy_preparation import LegacyPreparation


def build_store_order_service() -> StoreOrders:
    return StoreOrders(OracleGateway())


def build_preparation_service() -> LegacyPreparation:
    return LegacyPreparation(OracleGateway())


__all__=['router','store_order_service','build_store_order_service','preparation_service','build_preparation_service']

from .api.execution_routes import router as execution_router, execution_service
from .infrastructure.execution_progress import OrderExecution


def build_execution_service() -> OrderExecution:
    return OrderExecution(OracleGateway())

from .api.store_decision_routes import router as store_decision_router, store_admission_service
from .infrastructure.store_admission import StoreAdmission


def build_store_admission_service() -> StoreAdmission:
    return StoreAdmission(OracleGateway())

from .api.preparation_read_routes import router as preparation_read_router

from .infrastructure.order_fulfillment_read import OrderFulfillmentRead


def build_fulfillment_read_service(gateway: Any | None = None) -> OrderFulfillmentRead:
    return OrderFulfillmentRead(gateway if gateway is not None else OracleGateway())


__all__.append("build_fulfillment_read_service")


from .infrastructure.customer_order_read import CustomerOrderRead


def build_customer_order_read_service(gateway: Any | None = None) -> CustomerOrderRead:
    return CustomerOrderRead(gateway if gateway is not None else OracleGateway())


__all__.append("build_customer_order_read_service")

from .contracts_prepared_layout import PreparedLayoutPort, prepared_layout_service
from .api.prepared_layout_routes import router as prepared_layout_router
from .infrastructure.prepared_layout import PreparedLayout


def build_prepared_layout(gateway: Any, posting: Any) -> PreparedLayoutPort:
    return PreparedLayout(gateway, posting)

# Shared source-authority read boundary; native policy remains authoritative.
from .infrastructure.store_source_scope import assert_store_scope as assert_customer_order_warehouse

from .contracts_consolidation import ConsolidationPort, consolidation_service
from .api.consolidation_routes import router as consolidation_router
from .infrastructure.consolidation import ConsolidationPlans


def build_consolidation_service(gateway: Any) -> ConsolidationPort:
    return ConsolidationPlans(gateway)


def resume_wave_launch(gateway: Any, wave: int, operation: str, actor: str, post_launch: Callable[[], Any],
                       projection_factory: Callable[[Any], Any]) -> dict:
    result = run_wave_launch(wave, operation, actor, post_launch,
                            WaveContinuation(gateway, wave, operation, actor),
                            lambda bound, identity, user: launch_steps(bound, identity, user, projection_factory),
                            post_frozen_sources)
    receipt = read_launch_receipt(gateway, wave, operation, actor)
    return {**result, "wave_status": receipt["wave_status"] or "NOT_VISIBLE"}
