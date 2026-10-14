from typing import Any,Protocol

class StockSettingError(ValueError):
    def __init__(self,message: str,status: int) -> None:
        super().__init__(message);self.status=status

class StockCompatibilityPort(Protocol):
    def set_compatibility(self,enabled: bool,reason: str,actor: str) -> dict[str,Any]: ...

def stock_compatibility_service() -> StockCompatibilityPort:
    raise RuntimeError("Database-wide compatibility setting not wired")
