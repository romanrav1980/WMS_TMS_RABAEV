from datetime import date
from typing import Any,Protocol

class DayReconciliationPort(Protocol):
    def stock_conflicts(self,ware: int,metric: str,after: str | None,limit: int,actor: str) -> dict[str,Any]: ...
    def report(self,ware: int,day: date,region: str,actor: str) -> dict[str,Any]: ...

def day_reconciliation_service() -> DayReconciliationPort:
    raise RuntimeError("Day reconciliation not wired")
