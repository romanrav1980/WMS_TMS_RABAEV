from typing import Any, Protocol

class OperationFactPort(Protocol):
    def write(self,operation: int,fields: dict[str,Any],actor: str) -> dict[str,Any]: ...

def operation_fact_service() -> OperationFactPort:
    raise RuntimeError("Existing ARM fact service not wired")
