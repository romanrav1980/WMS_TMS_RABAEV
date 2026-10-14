from typing import Any,Protocol


class ReturnPutawayPort(Protocol):
    def configure(self,ware_id: int,supplier_target: str,disposal_target: str,expected_version: int,actor: str) -> dict[str,Any]: ...
    def pending(self,ware_id: int,actor: str,receipt_operation_id: str | None=None) -> list[dict[str,Any]]: ...
    def plan(self,operation_id: str,receipt_id: str,actor: str) -> dict[str,Any]: ...


def return_putaway_service() -> ReturnPutawayPort:
    raise RuntimeError("Return putaway not wired")
