from .oracle_gateway import OracleGateway
from .modules.inventory.public import TraceManifestPort,build_trace_manifest

def build_trace_manifest_service() -> TraceManifestPort:
    return build_trace_manifest(OracleGateway())
