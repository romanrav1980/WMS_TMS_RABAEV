from .oracle_gateway import OracleGateway
from .modules.finance.public import LogisticsExpensePort,build_logistics_expenses

def build_logistics_expense_service() -> LogisticsExpensePort:
    return build_logistics_expenses(OracleGateway())
