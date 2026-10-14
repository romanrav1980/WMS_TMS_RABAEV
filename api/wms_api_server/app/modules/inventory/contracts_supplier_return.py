from typing import Any,Protocol
from .contracts_store_returns import StoreReturnReceiveError

class SupplierReturnPort(Protocol):
    def prepare(self,operation_id: str,receipt_id: str,supplier_inn: str,reason: str,reference: str,actor: str) -> dict[str,Any]: ...
    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]: ...
    def suppliers(self) -> list[dict[str,Any]]: ...

def supplier_return_service() -> SupplierReturnPort:
    raise RuntimeError("Supplier return preparation not wired")
