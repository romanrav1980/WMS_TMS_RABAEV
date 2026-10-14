from .oracle_gateway import OracleGateway
from .modules.resources.public import WorkloadHistoryPort, build_workload_history

def attendance_history() -> WorkloadHistoryPort:
    return build_workload_history(OracleGateway())
