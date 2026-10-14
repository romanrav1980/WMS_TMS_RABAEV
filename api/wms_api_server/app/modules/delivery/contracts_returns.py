from typing import Any,Protocol


class StoreReturnsPort(Protocol):
    def reuse_preview(self,receipt_id: str,line_no: int,quantity: str,actor: str) -> dict[str,Any]: ...
    def approve(self,operation_id: str,receipt_id: str,line_no: int,metadata: dict[str,Any],actor: str) -> dict[str,Any]: ...
    def original(self,receipt_id: str,actor: str|None=None) -> dict[str,Any]: ...


def store_returns_service() -> StoreReturnsPort:
    raise RuntimeError("Store returns service not wired")
