from .oracle_gateway import OracleGateway
from .modules.inventory.public import SupplierReturnPort,build_supplier_return

def build_supplier_return_service() -> SupplierReturnPort:
    return build_supplier_return(OracleGateway())
