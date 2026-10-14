from datetime import date
from decimal import Decimal
from typing import Any,Protocol

class SlottingError(RuntimeError):
    def __init__(self,code: str,message: str,status: int=409) -> None:
        super().__init__(message);self.code=code;self.status=status

class SlottingDemandPort(Protocol):
    def preview(self,ware: int,article: str,start: date,end: date,forecast: Decimal|None,forecast_unit: str|None,actor: str,pallet_weight: Decimal|None=None,costs: list[dict[str,Any]]|None=None,candidate_route: int|None=None) -> dict[str,Any]: ...

def slotting_demand_service() -> SlottingDemandPort:
    raise RuntimeError("Slotting source reader not wired")
