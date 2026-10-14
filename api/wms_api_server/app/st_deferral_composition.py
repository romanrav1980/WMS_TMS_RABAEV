from .oracle_gateway import OracleGateway
from .modules.transport.public import build_st_deferral,StDeferralPort

def build_st_deferral_service() -> StDeferralPort:
    return build_st_deferral(OracleGateway())
