from .oracle_gateway import OracleGateway
from .modules.resources.public import WorkloadConfigPort,build_workload_config

def workload_service() -> WorkloadConfigPort:
    return build_workload_config(OracleGateway())

from .modules.resources.public import WorkloadMonitorPort,build_workload_monitor

def workload_monitor() -> WorkloadMonitorPort:
    return build_workload_monitor(OracleGateway())

from .modules.resources.public import WaveTimePort,build_wave_time

def wave_time() -> WaveTimePort:
    return build_wave_time(OracleGateway())
