"""Same native fact writer and existing availability-cache invalidation."""
from collections.abc import Callable
from typing import Any
from ....oracle_gateway import OracleGateway
from .operation_fact import update_existing_operation_fact

class OperationFacts:
    def __init__(self,gateway: OracleGateway,on_success: Callable[[],None]) -> None:
        self.gateway=gateway;self.on_success=on_success
    def write(self,operation: int,fields: dict[str,Any],actor: str) -> dict[str,Any]:
        result=update_existing_operation_fact(self.gateway,operation,fields,actor)
        self.on_success()
        return result
