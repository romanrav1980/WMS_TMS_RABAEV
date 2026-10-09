from ...oracle_gateway import OracleGateway
from .api.store_order_routes import router, store_order_service, preparation_service
from .infrastructure.store_orders import StoreOrders
from .infrastructure.legacy_preparation import LegacyPreparation


def build_store_order_service() -> StoreOrders:
    return StoreOrders(OracleGateway())


def build_preparation_service() -> LegacyPreparation:
    return LegacyPreparation(OracleGateway())


__all__=['router','store_order_service','build_store_order_service','preparation_service','build_preparation_service']
