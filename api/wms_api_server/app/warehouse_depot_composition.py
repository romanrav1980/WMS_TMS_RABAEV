from .oracle_gateway import OracleGateway
from .modules.transport.public import build_warehouse_depot,WarehouseDepotPort
def build_warehouse_depot_service() -> WarehouseDepotPort:
    return build_warehouse_depot(OracleGateway())
