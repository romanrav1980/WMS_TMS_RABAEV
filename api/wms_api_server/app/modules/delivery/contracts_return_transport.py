from typing import Any,Protocol


class ReturnTransportPort(Protocol):
    def plan(self,operation_id: str,approval_id: str,metadata: dict[str,Any],actor: str) -> dict[str,Any]: ...
    def eligible(self) -> list[dict[str,Any]]: ...
    def trip(self,task_id: int) -> list[dict[str,Any]]: ...


def return_transport_service() -> ReturnTransportPort:
    raise RuntimeError("Return transport not wired")
