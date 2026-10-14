from .oracle_gateway import OracleGateway
from .modules.inventory.public import StockCompatibilityPort,build_stock_compatibility

def stock_settings_service() -> StockCompatibilityPort:
    return build_stock_compatibility(OracleGateway())
