from .oracle_gateway import OracleGateway
from .modules.inventory.public import RangeProposalPort,build_range_proposal

def range_proposal() -> RangeProposalPort:
    return build_range_proposal(OracleGateway())
