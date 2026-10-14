from .oracle_gateway import OracleGateway
from .modules.inventory.public import SlottingDemandPort,build_slotting_demand

def slotting_demand() -> SlottingDemandPort:
    return build_slotting_demand(OracleGateway())
