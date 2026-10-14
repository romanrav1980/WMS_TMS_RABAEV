from typing import Any,Protocol
from datetime import datetime

class WorkloadError(RuntimeError):
    def __init__(self,code: str,message: str,status: int=409) -> None:
        super().__init__(message);self.code=code;self.status=status

class WorkloadConfigPort(Protocol):
    def command(self,operation: str,action: str,body: dict[str,Any],actor: str) -> dict[str,Any]: ...
    def configuration(self,ware: int,actor: str,site: str | None=None,start: datetime | None=None,finish: datetime | None=None) -> dict[str,Any]: ...

def workload_config_service() -> WorkloadConfigPort:
    raise RuntimeError("Workload configuration not wired")

class WorkloadHistoryPort(Protocol):
    def read(self,ware: int,plan: str,limit: int,actor: str) -> dict[str,Any]: ...

def workload_history_service() -> WorkloadHistoryPort:
    raise RuntimeError("Attendance history not wired")
