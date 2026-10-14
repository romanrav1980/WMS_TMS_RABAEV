from .oracle_gateway import OracleGateway
from .modules.finance.public import ExpenseAllocationPort,build_expense_allocation

def build_expense_allocation_service() -> ExpenseAllocationPort:
    return build_expense_allocation(OracleGateway())
