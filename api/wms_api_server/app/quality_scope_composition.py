from .oracle_gateway import OracleGateway
from .modules.inventory.public import QualityScopePort,build_quality_scope

def quality_scope() -> QualityScopePort:
    return build_quality_scope(OracleGateway())
