"""Original availability cache and native writer wired at application composition."""
from .oracle_gateway import OracleGateway
from .services.transport_service import _clear_vehicle_availability_cache
from .modules.transport.public import OperationFactPort, OperationFacts

def build_operation_fact_service() -> OperationFactPort:
    return OperationFacts(OracleGateway(),_clear_vehicle_availability_cache)
