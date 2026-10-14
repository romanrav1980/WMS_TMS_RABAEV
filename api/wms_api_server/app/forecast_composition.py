from .oracle_gateway import OracleGateway
from .modules.transport.public import build_warehouse_forecast, WarehouseForecastPort

def forecast_service() -> WarehouseForecastPort:
    return build_warehouse_forecast(OracleGateway())
