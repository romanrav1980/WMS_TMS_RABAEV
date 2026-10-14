from .oracle_gateway import OracleGateway
from .modules.transport.public import VehicleProfilePort,build_vehicle_profiles

def build_vehicle_profile_service()->VehicleProfilePort:
    return build_vehicle_profiles(OracleGateway())
