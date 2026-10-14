from .oracle_gateway import OracleGateway
from .modules.inventory.public import InterwarehousePort,build_interwarehouse

def build_interwarehouse_service() -> InterwarehousePort:
    return build_interwarehouse(OracleGateway())
