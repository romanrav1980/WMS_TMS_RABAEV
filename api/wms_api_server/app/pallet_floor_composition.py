from .oracle_gateway import OracleGateway
from .modules.inventory.public import PalletFloorPort,build_pallet_floor_type,build_stock_posting_service

def build_pallet_floor_service()->PalletFloorPort:
    return build_pallet_floor_type(OracleGateway(),build_stock_posting_service())
