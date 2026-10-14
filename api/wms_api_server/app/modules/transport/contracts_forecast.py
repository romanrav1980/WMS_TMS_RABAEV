from dataclasses import dataclass
from typing import Any,Protocol

class WarehouseForecastError(RuntimeError):
    def __init__(self,code: str,message: str,status: int=409) -> None:
        self.code=code
        self.status=status
        super().__init__(message)

@dataclass(frozen=True)
class ForecastQuery:
    history_days: int=28
    horizon_days: int=7
    minimum_active_days: int=3
    include_current_day: bool=False
    scope: str="CASE_DISPATCH"

class WarehouseForecastPort(Protocol):
    def project(self,ware: int,limit: int,actor: str) -> dict[str,Any]: ...
    def project_load(self,load_id: str,actor: str) -> dict[str,Any]: ...
    def get(self,ware: int,query: ForecastQuery,actor: str) -> dict[str,Any]: ...

def warehouse_forecast_service() -> WarehouseForecastPort:
    raise RuntimeError("Warehouse forecast service not wired")
