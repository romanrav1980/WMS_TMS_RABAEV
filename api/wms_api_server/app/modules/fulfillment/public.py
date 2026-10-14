from typing import Any
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
