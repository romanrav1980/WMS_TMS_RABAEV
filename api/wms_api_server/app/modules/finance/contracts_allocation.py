from typing import Any,Protocol

class ExpenseAllocationPort(Protocol):
    def allocate(self,operation_id: str,expense_id: str,actor: str) -> dict[str,Any]: ...
    def invoice(self,invoice_id: int,actor: str) -> list[dict[str,Any]]: ...

def expense_allocation_service() -> ExpenseAllocationPort:
    raise RuntimeError("Expense allocation not wired")
