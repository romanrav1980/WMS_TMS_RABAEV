from .oracle_gateway import OracleGateway
from .modules.inventory.public import SupplierHandoverPort,build_supplier_handover

def build_supplier_handover_service() -> SupplierHandoverPort:
    return build_supplier_handover(OracleGateway())
