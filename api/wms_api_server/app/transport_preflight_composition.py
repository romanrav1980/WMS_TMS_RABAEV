from .oracle_gateway import OracleGateway
from .modules.transport.public import TransportPreflight, TransportPreflightPort


def preflight_service() -> TransportPreflightPort:
    return TransportPreflight(OracleGateway())
