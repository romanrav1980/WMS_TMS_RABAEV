from .oracle_gateway import OracleGateway
from .modules.inventory.public import ReturnDisposalPort,build_return_disposal

def build_return_disposal_service() -> ReturnDisposalPort:
    return build_return_disposal(OracleGateway())
