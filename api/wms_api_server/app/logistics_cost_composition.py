from .oracle_gateway import OracleGateway
from .modules.finance.public import LogisticsCostPort,build_logistics_costs

def build_logistics_cost_service() -> LogisticsCostPort:
    return build_logistics_costs(OracleGateway())
